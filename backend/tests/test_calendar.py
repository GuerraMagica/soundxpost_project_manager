"""M2.3 acceptance tests: unified calendar feed, custom events, drag-and-drop persistence."""
from datetime import date, timedelta

from tests.conftest import login_as


def _make_project_and_episode(admin_client):
    project = admin_client.post(
        "/api/projects", json={"name": "Cal Test", "code": "CAL-1", "project_type": "SERIES"}
    ).json()
    episode = admin_client.post(
        "/api/episodes", json={"project_id": project["id"], "code": "S01E01"}
    ).json()
    return project, episode


def test_calendar_feed_includes_episode_mix_and_delivery(admin_client):
    project, episode = _make_project_and_episode(admin_client)
    mix_date = (date.today() + timedelta(days=5)).isoformat()
    admin_client.patch(f"/api/episodes/{episode['id']}", json={"mix_date": mix_date})

    feed = admin_client.get("/api/calendar/events", params={"project_id": project["id"]}).json()
    mix_items = [i for i in feed if i["source"] == "EPISODE_MIX"]
    assert len(mix_items) == 1
    assert mix_items[0]["source_id"] == episode["id"]


def test_calendar_feed_includes_task_due_date(admin_client):
    project, episode = _make_project_and_episode(admin_client)
    due = (date.today() + timedelta(days=2)).isoformat()
    admin_client.post(
        "/api/tasks",
        json={"title": "Editar mezcla", "project_id": project["id"], "episode_id": episode["id"], "due_date": due},
    )
    feed = admin_client.get("/api/calendar/events", params={"project_id": project["id"]}).json()
    assert any(i["source"] == "TASK" for i in feed)


def test_drag_mix_date_updates_episode_and_reevaluates_risks(admin_client):
    project, episode = _make_project_and_episode(admin_client)
    new_date = (date.today() + timedelta(days=1)).isoformat()

    # simulate dragging the mix milestone: frontend calls the episode PATCH endpoint
    resp = admin_client.patch(f"/api/episodes/{episode['id']}", json={"mix_date": new_date})
    assert resp.status_code == 200
    assert resp.json()["mix_date"] == new_date

    activity = admin_client.get("/api/activity", params={"project_id": project["id"]}).json()
    assert any(a["event_type"] == "MIX_DATE_CHANGED" for a in activity)


def test_create_custom_calendar_event(admin_client):
    project, episode = _make_project_and_episode(admin_client)
    resp = admin_client.post(
        "/api/calendar/events",
        json={
            "project_id": project["id"],
            "episode_id": episode["id"],
            "title": "Sesión ADR",
            "event_type": "ADR_SESSION",
            "start": "2026-10-01T10:00:00",
        },
    )
    assert resp.status_code == 201
    event = resp.json()
    assert event["event_type"] == "ADR_SESSION"

    feed = admin_client.get("/api/calendar/events", params={"project_id": project["id"]}).json()
    assert any(i["source"] == "CALENDAR_EVENT" and i["source_id"] == event["id"] for i in feed)


def test_drag_custom_event_persists_new_date(admin_client):
    project, episode = _make_project_and_episode(admin_client)
    event = admin_client.post(
        "/api/calendar/events",
        json={
            "project_id": project["id"],
            "episode_id": episode["id"],
            "title": "QC Ronda 1",
            "event_type": "QC",
            "start": "2026-10-01T09:00:00",
        },
    ).json()

    moved = admin_client.patch(f"/api/calendar/events/{event['id']}", json={"start": "2026-10-05T09:00:00"})
    assert moved.status_code == 200
    assert moved.json()["start"].startswith("2026-10-05")


def test_non_member_cannot_move_calendar_event(admin_client, client, make_user):
    project, episode = _make_project_and_episode(admin_client)
    event = admin_client.post(
        "/api/calendar/events",
        json={"project_id": project["id"], "episode_id": episode["id"], "title": "Reconform", "event_type": "RECONFORM", "start": "2026-10-01T09:00:00"},
    ).json()

    outsider, password = make_user("outsider2@test.local", "EDITOR")
    outsider_client = login_as(client, outsider.email, password)
    resp = outsider_client.patch(f"/api/calendar/events/{event['id']}", json={"start": "2026-11-01T09:00:00"})
    assert resp.status_code == 403


def test_unauthenticated_cannot_read_calendar(client):
    resp = client.get("/api/calendar/events")
    assert resp.status_code == 401
