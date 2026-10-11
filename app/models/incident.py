from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Status(str, Enum):
    OPEN= "Open"
    INVESTIGATING = "Investigating"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class Incident(BaseModel):
    incident_id: str
    application: str
    model_name: str
    severity: Severity
    description: str
    status: Status
    timestamp: datetime

class IncidentCreate(BaseModel):
    application: str
    model_name: str
    severity: Severity
    description: str

class IncidentUpdate(BaseModel):
    application: str | None = None
    model_name: str | None = None
    severity: Severity | None = None
    description: str | None = None
    status: Status | None = None