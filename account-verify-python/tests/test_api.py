"""Tests for FastAPI web service - validates the REST API layer."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestVerifyEndpoint:
    """Tests for POST /api/verify endpoint."""

    def test_successful_verification(self, client: TestClient) -> None:
        """Valid credentials return ACCOUNT VERIFIED."""
        response = client.post(
            "/api/verify",
            json={"account_no": "1234567890", "pin": "4321"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "ACCOUNT VERIFIED"
        assert data["success"] is True

    def test_account_not_found(self, client: TestClient) -> None:
        """Wrong account number returns ACCOUNT NOT FOUND."""
        response = client.post(
            "/api/verify",
            json={"account_no": "0000000000", "pin": "4321"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "ACCOUNT NOT FOUND"
        assert data["success"] is False

    def test_invalid_pin(self, client: TestClient) -> None:
        """Wrong PIN returns INVALID PIN."""
        response = client.post(
            "/api/verify",
            json={"account_no": "1234567890", "pin": "0000"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "INVALID PIN"
        assert data["success"] is False

    def test_empty_account_no(self, client: TestClient) -> None:
        """Empty account number returns ACCOUNT NOT FOUND."""
        response = client.post(
            "/api/verify",
            json={"account_no": "", "pin": "4321"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "ACCOUNT NOT FOUND"
        assert data["success"] is False

    def test_empty_pin(self, client: TestClient) -> None:
        """Empty PIN with valid account returns INVALID PIN."""
        response = client.post(
            "/api/verify",
            json={"account_no": "1234567890", "pin": ""},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "INVALID PIN"
        assert data["success"] is False


class TestVerifyEndpointValidation:
    """Tests for request validation on POST /api/verify."""

    def test_missing_account_no(self, client: TestClient) -> None:
        """Missing account_no should return 422."""
        response = client.post(
            "/api/verify",
            json={"pin": "4321"},
        )
        assert response.status_code == 422

    def test_missing_pin(self, client: TestClient) -> None:
        """Missing pin should return 422."""
        response = client.post(
            "/api/verify",
            json={"account_no": "1234567890"},
        )
        assert response.status_code == 422

    def test_missing_body(self, client: TestClient) -> None:
        """Missing request body should return 422."""
        response = client.post("/api/verify")
        assert response.status_code == 422

    def test_account_no_too_long(self, client: TestClient) -> None:
        """Account number exceeding PIC X(10) should return 422."""
        response = client.post(
            "/api/verify",
            json={"account_no": "12345678901", "pin": "4321"},
        )
        assert response.status_code == 422

    def test_pin_too_long(self, client: TestClient) -> None:
        """PIN exceeding PIC X(4) should return 422."""
        response = client.post(
            "/api/verify",
            json={"account_no": "1234567890", "pin": "43210"},
        )
        assert response.status_code == 422

    def test_get_method_not_allowed(self, client: TestClient) -> None:
        """GET on /api/verify should return 405."""
        response = client.get("/api/verify")
        assert response.status_code == 405

    def test_wrong_content_type(self, client: TestClient) -> None:
        """Non-JSON content type should return 422."""
        response = client.post(
            "/api/verify",
            content="account_no=1234567890&pin=4321",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 422


class TestAPIDocumentation:
    """Tests for API documentation endpoints."""

    def test_openapi_schema(self, client: TestClient) -> None:
        """OpenAPI schema should be accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "Account Verification Service"
        assert "/api/verify" in schema["paths"]

    def test_docs_endpoint(self, client: TestClient) -> None:
        """Swagger UI docs should be accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
