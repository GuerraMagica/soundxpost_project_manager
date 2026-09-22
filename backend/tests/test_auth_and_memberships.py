"""M2.2 acceptance tests: users, project memberships, and permission enforcement."""
from tests.conftest import login_as


def test_login_and_me(admin_client):
    resp = admin_client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["role"] == "ADMIN"


def test_login_rejects_wrong_password(client, make_user):
    make_user("someone@test.local", "EDITOR", password="CorrectPass1!")
    resp = client.post("/api/auth/login", json={"email": "someone@test.local", "password": "wrong"})
    assert resp.status_code == 401


def test_unauthenticated_request_is_rejected(client):
    resp = client.post("/api/projects", json={"name": "X", "code": "X-1", "project_type": "SERIES"})
    assert resp.status_code == 401


def test_admin_can_create_user_and_assign_to_multiple_projects(admin_client, make_user):
    p1 = admin_client.post("/api/projects", json={"name": "P1", "code": "P-1", "project_type": "SERIES"}).json()
    p2 = admin_client.post("/api/projects", json={"name": "P2", "code": "P-2", "project_type": "SERIES"}).json()

    created = admin_client.post(
        "/api/users",
        json={"name": "Multi Editor", "email": "multi@test.local", "role": "EDITOR", "password": "Passw0rd!"},
    )
    assert created.status_code == 201
    user_id = created.json()["id"]

    for project in (p1, p2):
        member = admin_client.post(f"/api/projects/{project['id']}/members", json={"user_id": user_id})
        assert member.status_code == 201

    projects = admin_client.get(f"/api/users/{user_id}/projects").json()
    assert {p["id"] for p in projects} == {p1["id"], p2["id"]}


def test_non_member_is_denied_access_to_project_write(admin_client, client, make_user):
    project = admin_client.post("/api/projects", json={"name": "Restricted", "code": "R-1", "project_type": "SERIES"}).json()

    editor, password = make_user("outsider@test.local", "EDITOR")
    outsider_client = login_as(client, editor.email, password)

    resp = outsider_client.post(
        "/api/episodes", json={"project_id": project["id"], "code": "S01E01"}
    )
    assert resp.status_code == 403


def test_member_with_operational_role_can_write(admin_client, client, make_user):
    project = admin_client.post("/api/projects", json={"name": "Open", "code": "O-1", "project_type": "SERIES"}).json()

    editor, password = make_user("member@test.local", "EDITOR")
    admin_client.post(f"/api/projects/{project['id']}/members", json={"user_id": editor.id})

    member_client = login_as(client, editor.email, password)
    resp = member_client.post("/api/episodes", json={"project_id": project["id"], "code": "S01E01"})
    assert resp.status_code == 201


def test_viewer_role_cannot_create_task(admin_client, client, make_user):
    project = admin_client.post("/api/projects", json={"name": "ViewProj", "code": "V-1", "project_type": "SERIES"}).json()
    viewer, password = make_user("viewer@test.local", "VIEWER")
    admin_client.post(f"/api/projects/{project['id']}/members", json={"user_id": viewer.id})

    viewer_client = login_as(client, viewer.email, password)
    resp = viewer_client.post("/api/tasks", json={"title": "No permitido", "project_id": project["id"]})
    assert resp.status_code == 403


def test_only_admin_can_create_users(admin_client, client, make_user):
    editor, password = make_user("cannot-create@test.local", "EDITOR")
    editor_client = login_as(client, editor.email, password)
    resp = editor_client.post(
        "/api/users", json={"name": "X", "email": "x@test.local", "role": "EDITOR", "password": "Passw0rd!"}
    )
    assert resp.status_code == 403
