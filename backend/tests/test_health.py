from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_application_starts():
    """Verify that the FastAPI application responds to requests."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_dashboard_summary():
    """Verify that the dashboard summary endpoint responds successfully."""
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200


def test_audit_chain_verification():
    """Verify that the audit verification endpoint responds successfully."""
    response = client.get("/api/compliance-rules/audit/verify")
    assert response.status_code == 200

    data = response.json()
    assert "valid" in data

def test_public_trace_existing_package():
    response = client.get("/api/public/trace/TEA-PKG-0002")

    assert response.status_code == 200
    data = response.json()
    assert data["trace_status"] == "TRACEABLE"
    assert data["package"]["package_code"] == "PKG-0002"


def test_public_trace_unknown_qr():
    response = client.get("/api/public/trace/UNKNOWN-QR-CODE")

    assert response.status_code == 404