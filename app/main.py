from fastapi import FastAPI, status, Depends, HTTPException
from pydantic import ValidationError
from app.models.incident import Incident, IncidentCreate, IncidentUpdate
from app.services.incident_service import create_incident, get_incidents, get_incident_by_id, update_incident
from app.db.incident_repository import IncidentRepository
from app.config.dependencies import get_repository

app = FastAPI(
    title="AegisOps",
    description="Autonomous LLMOps Platform",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "service": "AegisOps",
        "status": "running" 
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.post(
    "/incidents",
    status_code=status.HTTP_201_CREATED,
    response_model=Incident
)
def create_incident_endpoint(incident: IncidentCreate, repository: IncidentRepository = Depends(get_repository)):
    return create_incident(incident, repository)

@app.get(
    "/incidents",
    response_model=list[Incident]
)
def get_incidents_endpoint(repository: IncidentRepository = Depends(get_repository)):
    return get_incidents(repository)

@app.get(
    "/incidents/{incident_id}", response_model=Incident)
def get_incident_endpoint(incident_id: str, repository: IncidentRepository = Depends(get_repository)):
    incident = get_incident_by_id(
        incident_id,
        repository
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )
    return incident

@app.patch(
    "/incidents/{incident_id}",
    response_model=Incident
)
def update_incident_endpoint(
    incident_id: str,
    update: IncidentUpdate,
    repository: IncidentRepository = Depends(get_repository)
):
    try:
        incident = update_incident(
            incident_id,
            update,
            repository
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())


    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )
    return incident