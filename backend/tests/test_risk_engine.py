"""Tests for the deterministic risk engine: detection + idempotency."""
from datetime import date, timedelta

from app import models
from app.risk_engine.rules import run_risk_engine


def _make_project(db):
    project = models.Project(name="Test Project", code="T-001", project_type="SERIES")
    db.add(project)
    db.flush()
    return project


def test_mix_without_adr_composite_creates_risk(db_session):
    db = db_session
    project = _make_project(db)
    episode = models.Episode(project_id=project.id, code="S01E01", mix_date=date.today() + timedelta(days=2))
    db.add(episode)
    db.flush()
    db.add(
        models.ADREntry(
            project_id=project.id, episode_id=episode.id, character_name="Alice",
            convocatoria=1, status="GRABADO",
        )
    )
    db.commit()

    result = run_risk_engine(db)
    assert result["created"] == 2  # MIX_WITHOUT_ADR_COMPOSITE + ADR_RECORDED_NOT_RECEIVED

    risks = db.query(models.Risk).all()
    rule_ids = {r.rule_id for r in risks}
    assert "MIX_WITHOUT_ADR_COMPOSITE" in rule_ids
    assert "ADR_RECORDED_NOT_RECEIVED" in rule_ids


def test_risk_engine_is_idempotent(db_session):
    db = db_session
    project = _make_project(db)
    episode = models.Episode(project_id=project.id, code="S01E01", mix_date=date.today() + timedelta(days=2))
    db.add(episode)
    db.flush()
    db.add(
        models.ADREntry(
            project_id=project.id, episode_id=episode.id, character_name="Alice",
            convocatoria=1, status="GRABADO",
        )
    )
    db.commit()

    run_risk_engine(db)
    total_after_first_run = db.query(models.Risk).count()

    run_risk_engine(db)
    total_after_second_run = db.query(models.Risk).count()

    assert total_after_first_run == total_after_second_run == 2


def test_risk_auto_closes_when_condition_resolved(db_session):
    db = db_session
    project = _make_project(db)
    episode = models.Episode(project_id=project.id, code="S01E01", mix_date=date.today() + timedelta(days=2))
    db.add(episode)
    db.flush()
    adr = models.ADREntry(
        project_id=project.id, episode_id=episode.id, character_name="Alice",
        convocatoria=1, status="GRABADO",
    )
    db.add(adr)
    db.commit()

    run_risk_engine(db)
    open_risk = (
        db.query(models.Risk).filter(models.Risk.rule_id == "ADR_RECORDED_NOT_RECEIVED").first()
    )
    assert open_risk.status == "DETECTED"

    adr.status = "FINALIZADO"
    db.commit()
    run_risk_engine(db)

    db.refresh(open_risk)
    assert open_risk.status == "CLOSED"


def test_output_approved_missing_from_delivery(db_session):
    db = db_session
    project = _make_project(db)
    episode = models.Episode(project_id=project.id, code="S01E01")
    db.add(episode)
    db.flush()
    db.add(
        models.Output(
            project_id=project.id, episode_id=episode.id, material_type="PM_VO_5_1",
            version="V01", status="PASSED",
        )
    )
    db.commit()

    result = run_risk_engine(db)
    assert result["created"] == 1
    risk = db.query(models.Risk).first()
    assert risk.rule_id == "OUTPUT_APPROVED_MISSING_FROM_DELIVERY"
    assert risk.severity == "HIGH"
