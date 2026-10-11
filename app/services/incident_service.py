from app.models.incident import Incident, IncidentCreate, Status, IncidentUpdate
from uuid import uuid4
from datetime import datetime, timezone
from app.db.incident_repository import IncidentRepository


def create_incident(incident: IncidentCreate, repository: IncidentRepository) -> Incident:
    return repository.save(
        Incident(
            incident_id=str(uuid4()),
            application=incident.application,
            model_name=incident.model_name,
            severity=incident.severity,
            description=incident.description,
            status=Status.OPEN,
            timestamp=datetime.now(timezone.utc)
        )
    )

def get_incidents(repository: IncidentRepository) -> list[Incident]:
    return repository.get_all()

def get_incident_by_id(incident_id: str, repository: IncidentRepository) -> Incident | None:
    return repository.get_by_id(incident_id)

def update_incident(incident_id: str, update: IncidentUpdate, repository: IncidentRepository) -> Incident | None:
    incident = repository.get_by_id(incident_id)
    if incident is None:
        return None

    update_data = update.model_dump(exclude_unset=True)
    # updated_incident = incident.model_copy(update=update_data)
    new_data = incident.model_dump() | update_data
    updated_incident = Incident.model_validate(new_data)
    return repository.update(updated_incident)