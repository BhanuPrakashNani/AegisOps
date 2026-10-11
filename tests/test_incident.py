from app.models.incident import Incident, IncidentCreate, IncidentUpdate
from app.services.incident_service import create_incident, get_incidents, get_incident_by_id, update_incident 
from app.db.incident_repository import IncidentRepository
from datetime import datetime, timezone
import json
import pytest
from pydantic import ValidationError

def test_create_incident():
    incident = IncidentCreate(
        application="AegisOps",
        model_name="gpt-5",
        severity="high",
        description="Latency increased"
    )
    repository = IncidentRepository()
    result = create_incident(incident, repository)

    assert result.application == "AegisOps"
    assert result.model_name == "gpt-5"
    assert result.severity == "high"
    assert result.description == "Latency increased"
    assert result.status == "Open"
    assert result.incident_id is not None
    assert result.timestamp is not None
    assert len(repository.get_all()) == 1
    assert repository.get_all()[0].incident_id == result.incident_id

def test_get_incidents():
    incident1 = Incident(
        incident_id="1",
        application="AegisOps1",
        model_name="gpt-5",
        severity="high",
        description="Latency increased",
        status="Open",
        timestamp=datetime.now(timezone.utc)
    )

    incident2 = Incident(
            incident_id="2",
            application="AegisOps2",
            model_name="gpt-5",
            severity="high",
            description="Latency increased",
            status="Open",
            timestamp=datetime.now(timezone.utc)
        )
    repository = IncidentRepository()
    repository.save(incident1)
    repository.save(incident2)
    result = get_incidents(repository)
    assert len(result) == 2
    assert result[0].incident_id == "1"
    assert result[1].incident_id == "2"
    assert result == [incident1, incident2]

def test_get_incident_by_id():
    incident1 = Incident(
        incident_id="1",
        application="AegisOps1",
        model_name="gpt-5",
        severity="high",
        description="Latency increased",
        status="Open",
        timestamp=datetime.now(timezone.utc)
    )
    repository = IncidentRepository()
    repository.save(incident1)
    result = get_incident_by_id("1", repository)
    assert result is not None
    assert result.incident_id == incident1.incident_id

def test_get_missing_incident():
    incident1 = Incident(
        incident_id="1",
        application="AegisOps1",
        model_name="gpt-5",
        severity="high",
        description="Latency increased",
        status="Open",
        timestamp=datetime.now(timezone.utc)
    )
    repository = IncidentRepository()
    repository.save(incident1)
    result = get_incident_by_id("999", repository)
    assert result is None

def test_update_incident():
    incident1 = Incident(
        incident_id="1",
        application="AegisOps1",
        model_name="gpt-5",
        severity="high",
        description="Latency increased",
        status="Open",
        timestamp=datetime.now(timezone.utc)
    )
    repository = IncidentRepository()
    repository.save(incident1)
    update = IncidentUpdate(status="Investigating")
    result = update_incident(incident1.incident_id, update=update, repository=repository)
    assert result is not None
    assert incident1.status == "Open"
    assert result.status == "Investigating"
    assert result.application == "AegisOps1"
    assert result.model_name == "gpt-5"
    assert result.severity == "high"
    assert result.description == "Latency increased"
    assert result.incident_id is not None
    assert result.timestamp is not None

    stored_incident = repository.get_by_id("1")
    assert stored_incident is not None
    assert stored_incident.status == "Investigating"

def test_update_missing_incident():
    repository = IncidentRepository()
    update = IncidentUpdate(status="Investigating")
    result = update_incident("1", update=update, repository=repository)
    assert result is None


def test_update_incident_null_severity_raises():
    incident1 = Incident(
        incident_id="1",
        application="AegisOps1",
        model_name="gpt-5",
        severity="high",
        description="Latency increased",
        status="Open",
        timestamp=datetime.now(timezone.utc)
    )
    repository = IncidentRepository()
    repository.save(incident1)
    update = IncidentUpdate(severity=None)

    with pytest.raises(ValidationError):
        update_incident("1", update=update, repository=repository)

    stored_incident = repository.get_by_id("1")
    assert stored_incident is not None
    assert stored_incident.severity == "high"
