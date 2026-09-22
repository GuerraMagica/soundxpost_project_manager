"""Seed fictional DEMO data for SOUND X-POST.

Everything created here is clearly marked `is_demo=True` and prefixed with
DEMO. No real project names, clients or credentials are used, per the
security requirements of the product spec.
"""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app import models
from app.activity import log_activity
from app.auth import hash_password
from app.database import Base, SessionLocal, engine

DEMO_PROJECT_CODE = "DEMO-S01"

# Lab-only password shared by all DEMO users. Never used outside this seed.
DEMO_PASSWORD = "DemoSoundXPost2026!"


def _get_or_create_user(db: Session, name: str, email: str, role: str, department: str | None = None) -> models.User:
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return user
    user = models.User(
        name=name,
        email=email,
        role=role,
        department=department,
        hashed_password=hash_password(DEMO_PASSWORD),
        is_active=True,
        is_demo=True,
    )
    db.add(user)
    db.flush()
    return user


def seed_demo_data() -> str:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(models.Project).filter(models.Project.code == DEMO_PROJECT_CODE).first()
        if existing:
            return "Los datos DEMO ya existen; no se ha creado nada nuevo."

        today = date.today()

        admin = _get_or_create_user(db, "DEMO Admin", "demo.admin@soundxpost.local", "ADMIN", "IT")
        supervisor = _get_or_create_user(db, "DEMO Sound Supervisor", "demo.supervisor@soundxpost.local", "SUPERVISOR", "Sonido")
        coordinator = _get_or_create_user(db, "DEMO Coordinator", "demo.coordinator@soundxpost.local", "COORDINATOR", "Postproducción")
        dialogue_editor = _get_or_create_user(db, "DEMO Dialogue Editor", "demo.dialogue@soundxpost.local", "EDITOR", "Edición de diálogos")
        foley_editor = _get_or_create_user(db, "DEMO Foley Editor", "demo.foley@soundxpost.local", "EDITOR", "Foley")
        mixer = _get_or_create_user(db, "DEMO Mixing Engineer", "demo.mixer@soundxpost.local", "MIXER", "Mezcla")
        qc_user = _get_or_create_user(db, "DEMO QC Specialist", "demo.qc@soundxpost.local", "QC", "QC")
        archive_user = _get_or_create_user(db, "DEMO Archive Specialist", "demo.archive@soundxpost.local", "ARCHIVE")

        project = models.Project(
            name="DEMO - Proyecto Ficticio de Serie",
            code=DEMO_PROJECT_CODE,
            project_type="SERIES",
            client_name="DEMO Productora Ficticia",
            delivery_platform="DEMO Plataforma de Streaming",
            status="ACTIVE",
            start_date=today - timedelta(days=60),
            end_date=today + timedelta(days=30),
            authorized_paths="/demo/smb/proyectos/DEMO-S01 (ficticio, no real)",
            notes="Proyecto 100% DEMO. Todos los datos son ficticios y se usan para validar el MVP.",
            is_demo=True,
        )
        db.add(project)
        db.flush()
        log_activity(
            db, project_id=project.id, event_type="PROJECT_CREATED", entity_type="PROJECT",
            entity_id=project.id, new_state="ACTIVE", source="DEMO_SEED",
        )

        # Membership: everyone except the admin (who has global access) is an
        # explicit member of the DEMO project, mirroring "a user can belong to
        # several projects" without inventing other DEMO projects in this MVP.
        for member, role_in_project in [
            (supervisor, "SUPERVISOR"),
            (coordinator, "COORDINATOR"),
            (dialogue_editor, "EDITOR"),
            (foley_editor, "EDITOR"),
            (mixer, "MIXER"),
            (qc_user, "QC"),
            (archive_user, "ARCHIVE"),
        ]:
            db.add(models.ProjectMembership(project_id=project.id, user_id=member.id, role_in_project=role_in_project))

        episodes: dict[str, models.Episode] = {}
        for i in range(1, 7):
            code = f"S01E{i:02d}"
            ep = models.Episode(
                project_id=project.id,
                code=code,
                title=f"DEMO Episodio {i}",
                order_index=i,
                mix_date=None,
                delivery_date=None,
                status="IN_PROGRESS",
                is_demo=True,
            )
            db.add(ep)
            db.flush()
            episodes[code] = ep
            log_activity(
                db, project_id=project.id, episode_id=ep.id, event_type="EPISODE_CREATED",
                entity_type="EPISODE", entity_id=ep.id, source="DEMO_SEED",
            )

        # --- S01E01: PM y M&E aprobados; entrega final. -----------------
        ep1 = episodes["S01E01"]
        ep1.delivery_date = today - timedelta(days=2)
        ep1.status = "DELIVERED"
        for material in ["PM_VO_5_1", "MNE_5_1"]:
            out = models.Output(
                project_id=project.id, episode_id=ep1.id, material_type=material,
                version="V01", status="PASSED", qc_round=1,
                approved_at=today - timedelta(days=5), is_demo=True,
            )
            db.add(out)
            pkg = models.DeliveryPackage(
                project_id=project.id, episode_id=ep1.id, material_type=material,
                version="V01", status="DELIVERED", is_demo=True,
            )
            db.add(pkg)

        # --- S01E02: M&E QC02 recibido y pendiente. ---------------------
        ep2 = episodes["S01E02"]
        ep2.delivery_date = today + timedelta(days=10)
        out2 = models.Output(
            project_id=project.id, episode_id=ep2.id, material_type="MNE_5_1",
            version="V02", status="IN_QC", qc_round=2, notes="QC02 recibido, pendiente de cierre.",
            is_demo=True,
        )
        db.add(out2)

        # --- S01E03: ADR grabado pero no recibido; mezcla próxima. ------
        ep3 = episodes["S01E03"]
        ep3.mix_date = today + timedelta(days=3)
        ep3.delivery_date = today + timedelta(days=15)
        adr3 = models.ADREntry(
            project_id=project.id, episode_id=ep3.id, character_name="DEMO Personaje Pepito",
            actor_name="DEMO Actor 1", convocatoria=1, total_cues=18, add_flag=False, tbw_flag=False,
            status="GRABADO", source="MANUAL", is_demo=True,
        )
        db.add(adr3)

        # --- S01E04: Output V02 aprobado y Delivery Package V01. --------
        ep4 = episodes["S01E04"]
        ep4.delivery_date = today + timedelta(days=6)
        out4 = models.Output(
            project_id=project.id, episode_id=ep4.id, material_type="PM_VO_5_1",
            version="V02", status="PASSED", qc_round=2, approved_at=today - timedelta(days=1),
            is_demo=True,
        )
        db.add(out4)
        pkg4 = models.DeliveryPackage(
            project_id=project.id, episode_id=ep4.id, material_type="PM_VO_5_1",
            version="V01", status="READY", notes="Pendiente de reconstruir con V02.", is_demo=True,
        )
        db.add(pkg4)

        # --- S01E05: Foley recibido y ADR pendiente de edición. ---------
        ep5 = episodes["S01E05"]
        ep5.mix_date = today + timedelta(days=20)
        adr5 = models.ADREntry(
            project_id=project.id, episode_id=ep5.id, character_name="DEMO Personaje Lupita",
            actor_name="DEMO Actor 2", convocatoria=1, total_cues=9, add_flag=True, tbw_flag=False,
            status="PENDIENTE EDICIÓN", source="MANUAL", is_demo=True,
        )
        db.add(adr5)
        task_foley = models.Task(
            title="DEMO Confirmar recepción de Foley",
            description="El Foley ha sido recibido; falta confirmar integración en sesión.",
            project_id=project.id, episode_id=ep5.id, discipline="FOLEY",
            assignee_id=foley_editor.id, status="EN PROGRESO", priority="NORMAL",
            due_date=today + timedelta(days=4), is_demo=True,
        )
        db.add(task_foley)

        # --- S01E06: Entrega pendiente de cuesheet. ---------------------
        ep6 = episodes["S01E06"]
        ep6.delivery_date = today + timedelta(days=8)

        db.flush()

        for ep in episodes.values():
            record = models.ArchiveRecord(
                project_id=project.id, episode_id=ep.id,
                pt_session="LISTO", pm="LISTO", mne="LISTO", stems="LISTO",
                cuesheet="LISTO" if ep.code != "S01E06" else "PENDIENTE",
                qc_docs="LISTO", dubbing_ad="N_A", is_demo=True,
            )
            db.add(record)

        demo_tasks = [
            ("DEMO Revisar convocatoria ADR pendiente", ep3, dialogue_editor, "PENDIENTE", "HIGH"),
            ("DEMO Confirmar cierre de QC02", ep2, qc_user, "EN PROGRESO", "HIGH"),
            ("DEMO Actualizar Delivery Package a V02", ep4, coordinator, "PENDIENTE", "URGENT"),
            ("DEMO Generar cuesheet de archivo", ep6, archive_user, "PENDIENTE", "NORMAL"),
            ("DEMO Confirmar mezcla final", ep1, mixer, "FINALIZADO", "NORMAL"),
        ]
        for title, ep, assignee, status, priority in demo_tasks:
            db.add(
                models.Task(
                    title=title, project_id=project.id, episode_id=ep.id,
                    discipline="COORDINACIÓN", assignee_id=assignee.id,
                    status=status, priority=priority,
                    due_date=today + timedelta(days=5), is_demo=True,
                )
            )

        db.commit()

        from app.risk_engine.rules import run_risk_engine

        result = run_risk_engine(db)
        return (
            "Datos DEMO creados correctamente. "
            f"Riesgos detectados en la primera evaluación: {result}. "
            f"Usuarios DEMO creados con contraseña '{DEMO_PASSWORD}' "
            "(demo.admin@soundxpost.local, demo.supervisor@soundxpost.local, ...)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    print(seed_demo_data())
