"""Deterministic, rule-based risk engine for SOUND X-POST.

No AI/ML involved. Each rule inspects current database state and yields
zero or more `RiskCandidate` objects. The engine then reconciles candidates
against existing open risks using a stable `dedupe_key` so the same
situation is never duplicated, and closes risks whose underlying condition
has disappeared.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app import models

MIX_LOOKAHEAD_DAYS = 5
DELIVERY_LOOKAHEAD_DAYS = 5


@dataclass
class RiskCandidate:
    rule_id: str
    project_id: int
    episode_id: Optional[int]
    severity: str
    title: str
    description: str
    evidence: str
    suggested_action: str
    dedupe_key: str
    due_date: Optional[date] = None
    owner_id: Optional[int] = None


def _episode_label(episode: models.Episode | None) -> str:
    return episode.code if episode else "N/A"


def rule_mix_without_adr_composite(db: Session) -> list[RiskCandidate]:
    """Mezcla próxima sin ADR Composite confirmado (no FINALIZADO/AÑADIDO EN SESIÓN)."""
    candidates: list[RiskCandidate] = []
    horizon = date.today() + timedelta(days=MIX_LOOKAHEAD_DAYS)
    episodes = (
        db.query(models.Episode)
        .filter(models.Episode.mix_date.isnot(None))
        .filter(models.Episode.mix_date <= horizon)
        .filter(models.Episode.mix_date >= date.today())
        .all()
    )
    for ep in episodes:
        pending = (
            db.query(models.ADREntry)
            .filter(models.ADREntry.episode_id == ep.id)
            .filter(models.ADREntry.status.notin_(["FINALIZADO", "EN MEZCLA", "CANCELADO", "N/A"]))
            .all()
        )
        if pending:
            names = ", ".join(f"{p.character_name} (conv. {p.convocatoria}): {p.status}" for p in pending)
            candidates.append(
                RiskCandidate(
                    rule_id="MIX_WITHOUT_ADR_COMPOSITE",
                    project_id=ep.project_id,
                    episode_id=ep.id,
                    severity="HIGH",
                    title=f"Mezcla próxima sin ADR Composite confirmado — {_episode_label(ep)}",
                    description=(
                        f"El episodio {_episode_label(ep)} tiene mezcla programada el {ep.mix_date} "
                        f"y existen convocatorias ADR sin finalizar."
                    ),
                    evidence=f"ADR pendiente: {names}",
                    suggested_action="Confirmar estado de ADR con el editor de diálogos antes de la mezcla.",
                    dedupe_key=f"MIX_WITHOUT_ADR_COMPOSITE:{ep.id}",
                    due_date=ep.mix_date,
                )
            )
    return candidates


def rule_adr_recorded_not_received(db: Session) -> list[RiskCandidate]:
    entries = db.query(models.ADREntry).filter(models.ADREntry.status == "GRABADO").all()
    candidates = []
    for e in entries:
        ep = db.get(models.Episode, e.episode_id)
        candidates.append(
            RiskCandidate(
                rule_id="ADR_RECORDED_NOT_RECEIVED",
                project_id=e.project_id,
                episode_id=e.episode_id,
                severity="WARNING",
                title=f"ADR grabado pero no recibido — {e.character_name} (conv. {e.convocatoria})",
                description=(
                    f"{e.character_name} tiene la convocatoria {e.convocatoria} marcada como GRABADO "
                    f"pero el material todavía no ha sido recibido por edición."
                ),
                evidence=f"Estado actual: {e.status} (episodio {_episode_label(ep)})",
                suggested_action="Solicitar el envío del material grabado al estudio/actor.",
                dedupe_key=f"ADR_RECORDED_NOT_RECEIVED:{e.id}",
            )
        )
    return candidates


def rule_output_approved_missing_from_delivery(db: Session) -> list[RiskCandidate]:
    outputs = db.query(models.Output).filter(models.Output.status == "PASSED").all()
    candidates = []
    for o in outputs:
        pkg = (
            db.query(models.DeliveryPackage)
            .filter(models.DeliveryPackage.episode_id == o.episode_id)
            .filter(models.DeliveryPackage.material_type == o.material_type)
            .first()
        )
        ep = db.get(models.Episode, o.episode_id)
        if pkg is None:
            candidates.append(
                RiskCandidate(
                    rule_id="OUTPUT_APPROVED_MISSING_FROM_DELIVERY",
                    project_id=o.project_id,
                    episode_id=o.episode_id,
                    severity="HIGH",
                    title=f"Output aprobado ausente del Delivery Package — {o.material_type} ({_episode_label(ep)})",
                    description=(
                        f"El output {o.material_type} versión {o.version} está APROBADO (PASSED) "
                        f"pero no existe ningún registro de Delivery Package para ese material."
                    ),
                    evidence=f"Output id={o.id}, status=PASSED, version={o.version}",
                    suggested_action="Añadir el material al Delivery Package correspondiente.",
                    dedupe_key=f"OUTPUT_APPROVED_MISSING_FROM_DELIVERY:{o.id}",
                )
            )
        elif pkg.version != o.version:
            candidates.append(
                RiskCandidate(
                    rule_id="DELIVERY_VERSION_MISMATCH",
                    project_id=o.project_id,
                    episode_id=o.episode_id,
                    severity="CRITICAL",
                    title=f"Delivery Package con versión anterior — {o.material_type} ({_episode_label(ep)})",
                    description=(
                        f"El último output aprobado es {o.version}, pero el Delivery Package "
                        f"contiene la versión {pkg.version}."
                    ),
                    evidence=f"Output id={o.id} (PASSED, {o.version}) vs Delivery Package id={pkg.id} ({pkg.version})",
                    suggested_action="Reconstruir el Delivery Package con la versión aprobada más reciente.",
                    dedupe_key=f"DELIVERY_VERSION_MISMATCH:{o.id}:{pkg.id}",
                )
            )
    return candidates


def rule_qc_pending_close_near_delivery(db: Session) -> list[RiskCandidate]:
    candidates = []
    horizon = date.today() + timedelta(days=DELIVERY_LOOKAHEAD_DAYS)
    outputs = db.query(models.Output).filter(models.Output.status == "IN_QC").all()
    for o in outputs:
        ep = db.get(models.Episode, o.episode_id)
        if ep and ep.delivery_date and date.today() <= ep.delivery_date <= horizon:
            candidates.append(
                RiskCandidate(
                    rule_id="QC_PENDING_CLOSE_NEAR_DELIVERY",
                    project_id=o.project_id,
                    episode_id=o.episode_id,
                    severity="HIGH",
                    title=f"QC pendiente de cierre cerca de la entrega — {o.material_type} ({_episode_label(ep)})",
                    description=(
                        f"El output {o.material_type} sigue EN QC (ronda {o.qc_round}) y la entrega "
                        f"está prevista para el {ep.delivery_date}."
                    ),
                    evidence=f"Output id={o.id}, status=IN_QC, qc_round={o.qc_round}",
                    suggested_action="Priorizar el cierre del QC o escalar al responsable de calidad.",
                    dedupe_key=f"QC_PENDING_CLOSE_NEAR_DELIVERY:{o.id}",
                    due_date=ep.delivery_date,
                )
            )
    return candidates


def rule_archive_missing_cuesheet(db: Session) -> list[RiskCandidate]:
    records = db.query(models.ArchiveRecord).filter(models.ArchiveRecord.cuesheet != "LISTO").all()
    candidates = []
    for r in records:
        ep = db.get(models.Episode, r.episode_id)
        candidates.append(
            RiskCandidate(
                rule_id="ARCHIVE_MISSING_CUESHEET",
                project_id=r.project_id,
                episode_id=r.episode_id,
                severity="WARNING",
                title=f"Archivo sin cuesheet — {_episode_label(ep)}",
                description=f"El registro de archivo del episodio {_episode_label(ep)} no tiene el cuesheet listo.",
                evidence=f"ArchiveRecord id={r.id}, cuesheet={r.cuesheet}",
                suggested_action="Generar y adjuntar el cuesheet antes de cerrar el archivo.",
                dedupe_key=f"ARCHIVE_MISSING_CUESHEET:{r.id}",
            )
        )
    return candidates


def rule_archive_missing_stems(db: Session) -> list[RiskCandidate]:
    records = db.query(models.ArchiveRecord).filter(models.ArchiveRecord.stems != "LISTO").all()
    candidates = []
    for r in records:
        ep = db.get(models.Episode, r.episode_id)
        candidates.append(
            RiskCandidate(
                rule_id="ARCHIVE_MISSING_STEMS",
                project_id=r.project_id,
                episode_id=r.episode_id,
                severity="WARNING",
                title=f"Archivo sin stems obligatorios — {_episode_label(ep)}",
                description=f"El registro de archivo del episodio {_episode_label(ep)} no tiene los stems listos.",
                evidence=f"ArchiveRecord id={r.id}, stems={r.stems}",
                suggested_action="Verificar y depositar los stems obligatorios antes de cerrar el archivo.",
                dedupe_key=f"ARCHIVE_MISSING_STEMS:{r.id}",
            )
        )
    return candidates


ALL_RULES = [
    rule_mix_without_adr_composite,
    rule_adr_recorded_not_received,
    rule_output_approved_missing_from_delivery,
    rule_qc_pending_close_near_delivery,
    rule_archive_missing_cuesheet,
    rule_archive_missing_stems,
]


def run_risk_engine(db: Session) -> dict:
    """Evaluate all rules, upsert risks idempotently, close resolved ones."""
    candidates: list[RiskCandidate] = []
    for rule in ALL_RULES:
        candidates.extend(rule(db))

    seen_keys = set()
    created, updated = 0, 0
    for c in candidates:
        seen_keys.add(c.dedupe_key)
        existing = db.query(models.Risk).filter(models.Risk.dedupe_key == c.dedupe_key).first()
        if existing is None:
            risk = models.Risk(
                rule_id=c.rule_id,
                project_id=c.project_id,
                episode_id=c.episode_id,
                severity=c.severity,
                title=c.title,
                description=c.description,
                evidence=c.evidence,
                suggested_action=c.suggested_action,
                owner_id=c.owner_id,
                due_date=c.due_date,
                status="DETECTED",
                dedupe_key=c.dedupe_key,
            )
            db.add(risk)
            created += 1
        else:
            existing.description = c.description
            existing.evidence = c.evidence
            existing.severity = c.severity
            existing.due_date = c.due_date
            existing.updated_at = datetime.utcnow()
            if existing.status == "CLOSED":
                existing.status = "DETECTED"
            updated += 1

    # Auto-close risks whose condition no longer holds (still auditable via status/history).
    open_risks = db.query(models.Risk).filter(models.Risk.status != "CLOSED").all()
    closed = 0
    for risk in open_risks:
        if risk.dedupe_key not in seen_keys:
            risk.status = "CLOSED"
            risk.updated_at = datetime.utcnow()
            closed += 1

    db.commit()
    return {"created": created, "updated": updated, "closed": closed, "evaluated": len(candidates)}
