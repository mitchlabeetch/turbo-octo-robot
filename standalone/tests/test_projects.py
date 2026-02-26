"""Tests for Project Management, Workflow, and Reporting."""

from datetime import date
from decimal import Decimal

from app.services.projects import ProjectService


class TestProjectService:

    def test_create_project(self, db_session):
        svc = ProjectService(db_session, tenant_id="default")
        project = svc.create_project({"name": "Due Diligence - Acme", "status": "active"})
        assert project.uuid is not None
        assert project.name == "Due Diligence - Acme"

    def test_create_task(self, db_session):
        svc = ProjectService(db_session, tenant_id="default")
        project = svc.create_project({"name": "Project X"})
        task = svc.create_task(project.id, {"title": "Review financials", "priority": "high"})
        assert task.project_id == project.id
        assert task.status == "todo"

    def test_log_time_updates_actual_hours(self, db_session, test_user):
        svc = ProjectService(db_session, tenant_id="default")
        project = svc.create_project({"name": "Time Project"})
        task = svc.create_task(project.id, {"title": "Analysis"})
        svc.log_time({"task_id": task.id, "user_id": test_user.id, "date": date(2026, 1, 15), "hours": 3.5})
        svc.log_time({"task_id": task.id, "user_id": test_user.id, "date": date(2026, 1, 16), "hours": 2.0})
        updated_task = svc.task_repo.get_by_id(task.id)
        assert updated_task.actual_hours == 5.5

    def test_list_projects_by_status(self, db_session):
        svc = ProjectService(db_session, tenant_id="default")
        svc.create_project({"name": "Active 1", "status": "active"})
        svc.create_project({"name": "Active 2", "status": "active"})
        svc.create_project({"name": "Done", "status": "completed"})
        active = svc.list_projects(status="active")
        assert len(active) == 2


class TestProjectEndpoints:

    def test_create_project_api(self, auth_client):
        resp = auth_client.post("/projects", json={"name": "API Project"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "API Project"

    def test_list_projects_api(self, auth_client):
        auth_client.post("/projects", json={"name": "P1"})
        auth_client.post("/projects", json={"name": "P2"})
        resp = auth_client.get("/projects")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_create_task_api(self, auth_client):
        project = auth_client.post("/projects", json={"name": "Task Project"}).json()
        resp = auth_client.post(f"/projects/{project['id']}/tasks", json={"title": "Review docs"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Review docs"

    def test_log_time_api(self, auth_client, test_user):
        resp = auth_client.post("/projects/time-entries", json={
            "user_id": test_user.id,
            "date": "2026-01-15",
            "hours": 4.0,
            "description": "Analysis work",
        })
        assert resp.status_code == 200
        assert resp.json()["hours"] == 4.0
