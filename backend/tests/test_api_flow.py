"""Basic API smoke tests: project -> episode -> task -> ADR full flow."""


def test_create_project_and_list(admin_client):
    resp = admin_client.post(
        "/api/projects",
        json={"name": "Serie API Test", "code": "API-001", "project_type": "SERIES"},
    )
    assert resp.status_code == 201
    project = resp.json()
    assert project["code"] == "API-001"

    resp = admin_client.get("/api/projects")
    assert resp.status_code == 200
    assert any(p["code"] == "API-001" for p in resp.json())


def test_duplicate_project_code_rejected(admin_client):
    payload = {"name": "Dup", "code": "API-DUP", "project_type": "SERIES"}
    assert admin_client.post("/api/projects", json=payload).status_code == 201
    resp = admin_client.post("/api/projects", json=payload)
    assert resp.status_code == 409


def test_episode_task_adr_flow(admin_client):
    project = admin_client.post(
        "/api/projects", json={"name": "Flow Test", "code": "API-FLOW", "project_type": "SERIES"}
    ).json()

    episode = admin_client.post(
        "/api/episodes", json={"project_id": project["id"], "code": "S01E01"}
    ).json()
    assert episode["project_id"] == project["id"]

    task = admin_client.post(
        "/api/tasks",
        json={"title": "Editar ADR", "project_id": project["id"], "episode_id": episode["id"]},
    ).json()
    assert task["status"] == "PENDIENTE"

    updated_task = admin_client.patch(f"/api/tasks/{task['id']}", json={"status": "FINALIZADO"}).json()
    assert updated_task["status"] == "FINALIZADO"
    assert updated_task["resolved_at"] is not None

    adr_entry = admin_client.post(
        "/api/adr",
        json={
            "project_id": project["id"],
            "episode_id": episode["id"],
            "character_name": "Test Character",
            "convocatoria": 1,
            "status": "GRABADO",
        },
    ).json()
    assert adr_entry["status"] == "GRABADO"

    risk_run = admin_client.post("/api/risks/run").json()
    assert risk_run["created"] >= 1

    risks = admin_client.get("/api/risks", params={"project_id": project["id"]}).json()
    assert any(r["rule_id"] == "ADR_RECORDED_NOT_RECEIVED" for r in risks)

    activity = admin_client.get("/api/activity", params={"project_id": project["id"]}).json()
    assert len(activity) > 0
