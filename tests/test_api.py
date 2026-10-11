from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.config.dependencies import get_repository
from app.db.incident_repository import IncidentRepository

client = TestClient(app)

@pytest.fixture
def test_repository():
    repository = IncidentRepository()
    app.dependency_overrides[get_repository] = lambda: repository

    yield repository
    app.dependency_overrides.clear()

def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "AegisOps",
        "status": "running"
    }

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }

def test_create_incident():
    response = client.post(
        "/incidents",
        json={
            "application": "AegisOps",
            "model_name": "gpt-5",
            "severity": "high",
            "description": "Latency increased"
        }
    )

    assert response.status_code == 201
    print(response.json())
    data = response.json()

    assert data["application"] == "AegisOps"
    assert data["model_name"] == "gpt-5"
    assert data["severity"] == "high"
    assert data["description"] == "Latency increased"
    assert data["status"] == "Open"
    assert data["incident_id"] is not None
    assert data["timestamp"] is not None

def test_get_incidents(test_repository):
    response = client.post(
            "/incidents",
            json={
                "application": "AegisOps2",
                "model_name": "gpt-5",
                "severity": "high",
                "description": "Latency increased"
            }
        )
    assert response.status_code == 201
    get_response= client.get("/incidents")
    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data) == 1
    assert data[0]["application"] == "AegisOps2"

def test_get_incident(test_repository):
    response = client.post(
                "/incidents",
                json={
                    "application": "AegisOps3",
                    "model_name": "gpt-5",
                    "severity": "high",
                    "description": "Latency increased"
                }
            )
    assert response.status_code == 201

    created_incident = response.json()
    incident_id = created_incident["incident_id"]
    get_incident_response = client.get(f"/incidents/{incident_id}")

    assert get_incident_response.status_code == 200
    data = get_incident_response.json()

    assert data["incident_id"] == incident_id
    assert data["application"] == "AegisOps3"
    assert data["model_name"] == "gpt-5"
    assert data["severity"] == "high"
    assert data["description"] == "Latency increased"
    assert data["status"] == "Open"

def test_get_missing_incident(test_repository):
    incident_id = 12345
    get_incident_response = client.get(f"/incidents/{incident_id}")

    assert get_incident_response.status_code == 404
    assert get_incident_response.json() == {
        "detail": "Incident not found"
    }

def test_create_incident_invalid_severity(test_repository):
    response = client.post(
        "/incidents",
        json={
            "application": "AegisOps",
            "model_name": "gpt-5",
            "severity": "SUPER_CRITICAL",
            "description": "Latency increased"
        }
    )
    assert response.status_code == 422
    print(response.json())
    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "severity"]

def test_create_incident_missing_field(test_repository):
    response = client.post(
        "/incidents",
        json={
            "application": "AegisOps",
            "model_name": "gpt-5",
            "description": "Latency increased"
        }
    )
    assert response.status_code == 422
    print(response.json())
    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "severity"]

def test_update_incident(test_repository):
    response = client.post(
            "/incidents",
            json={
                "application": "AegisOps",
                "model_name": "gpt-5",
                "severity": "high",
                "description": "Latency increased"
            }
        )
    assert response.status_code == 201
    data = response.json()
    incident_id = data["incident_id"]
    update_response = client.patch(
        f"/incidents/{incident_id}",
        json={
            "status": "Investigating"
        }
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["status"] == "Investigating"
    assert updated_data["application"] == "AegisOps"
    assert updated_data["model_name"] == "gpt-5"
    assert updated_data["severity"] == "high"
    assert updated_data["description"] == "Latency increased"
    assert updated_data["incident_id"] == incident_id

def test_update_incident_multiple(test_repository):
    response = client.post(
            "/incidents",
            json={
                "application": "AegisOps",
                "model_name": "gpt-5",
                "severity": "high",
                "description": "Latency increased"
            }
        )
    assert response.status_code == 201
    data = response.json()
    incident_id = data["incident_id"]
    update_response = client.patch(
        f"/incidents/{incident_id}",
        json={
            "severity": "critical",
            "status": "Investigating",
            "description": "Latency and error rate increased"
        }
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["status"] == "Investigating"
    assert updated_data["application"] == "AegisOps"
    assert updated_data["model_name"] == "gpt-5"
    assert updated_data["severity"] == "critical"
    assert updated_data["description"] == "Latency and error rate increased"
    assert updated_data["incident_id"] == incident_id
    assert updated_data["timestamp"] == data["timestamp"]

def test_patch_non_existent_incident(test_repository):
    response = client.patch(
        "/incidents/does-not-exist",
        json={
            "status": "Investigating"
        }
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Incident not found"
    }

def test_null_severity(test_repository):
    response = client.post(
            "/incidents",
            json={
                "application": "AegisOps",
                "model_name": "gpt-5",
                "severity": "high",
                "description": "Latency increased"
            }
        )
    assert response.status_code == 201
    data = response.json()
    incident_id = data["incident_id"]
    update_response = client.patch(
        f"/incidents/{incident_id}",
        json={
            "severity": None
        }
    )
    assert update_response.status_code == 422

    get_response = client.get(f"/incidents/{incident_id}")
    assert get_response.status_code == 200
    stored = get_response.json()
    assert stored["severity"] == "high"
    assert stored["incident_id"] == incident_id
