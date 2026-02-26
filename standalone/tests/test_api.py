"""Tests for API endpoints."""


class TestHealthEndpoint:
    """Verify the health check endpoint."""

    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestCompanyEndpoints:
    """Verify company CRUD API."""

    def test_create_company(self, auth_client):
        response = auth_client.post("/companies", json={
            "name": "API Corp",
            "sector": "Technology"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "API Corp"
        assert "id" in data

    def test_get_company(self, auth_client):
        create_resp = auth_client.post("/companies", json={"name": "GetMe"})
        company_id = create_resp.json()["id"]
        response = auth_client.get(f"/companies/{company_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "GetMe"

    def test_company_not_found(self, auth_client):
        response = auth_client.get("/companies/99999")
        assert response.status_code == 404

    def test_duplicate_company(self, auth_client):
        auth_client.post("/companies", json={"name": "Unique Corp"})
        response = auth_client.post("/companies", json={"name": "Unique Corp"})
        assert response.status_code == 409


class TestContactEndpoints:
    """Verify contact CRUD API."""

    def test_create_contact(self, auth_client):
        response = auth_client.post("/contacts", json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@corp.com"
        })
        assert response.status_code == 200
        assert response.json()["email"] == "jane@corp.com"

    def test_duplicate_contact(self, auth_client):
        auth_client.post("/contacts", json={
            "first_name": "A", "last_name": "B", "email": "dup@test.com"
        })
        response = auth_client.post("/contacts", json={
            "first_name": "C", "last_name": "D", "email": "dup@test.com"
        })
        assert response.status_code == 409
