from app.db.incident_repository import IncidentRepository


repository = IncidentRepository()

def get_repository():
    return repository