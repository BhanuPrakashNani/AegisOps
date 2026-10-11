from app.models.incident import Incident


class IncidentRepository:

    def __init__(self):
        self.incidents = []

    def save(self, incident: Incident) -> Incident:
        self.incidents.append(incident)
        return incident

    def get_all(self) -> list[Incident]:
        return self.incidents

    def get_by_id(self, incident_id: str) -> Incident | None:
        for incident in self.incidents:
            if incident.incident_id == incident_id:
                return incident

        return None
    
    def update(self, incident: Incident) -> Incident:
        for index, existing_incident in enumerate(self.incidents):
            if existing_incident.incident_id == incident.incident_id:
                self.incidents[index] = incident
                return incident

        return None