from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.incident import IncidentType, IncidentSeverity


class IncidentCreate(BaseModel):
    incident_type: IncidentType
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    location: Optional[str] = None
    driver_id: Optional[str] = None
    load_id: Optional[str] = None
    truck_id: Optional[str] = None
    occurred_at: Optional[datetime] = None


class IncidentUpdate(BaseModel):
    incident_type: Optional[IncidentType] = None
    severity: Optional[IncidentSeverity] = None
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    driver_id: Optional[str] = None
    load_id: Optional[str] = None
    truck_id: Optional[str] = None
    ai_recommended_action: Optional[str] = None
    resolution_notes: Optional[str] = None


class IncidentResolve(BaseModel):
    resolution_notes: str = Field(..., min_length=1)


class IncidentResponse(BaseModel):
    id: str
    incident_number: str
    incident_type: IncidentType
    severity: IncidentSeverity
    title: str
    description: str
    location: Optional[str]
    driver_id: Optional[str]
    load_id: Optional[str]
    truck_id: Optional[str]
    ai_recommended_action: Optional[str]
    is_resolved: bool
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    occurred_at: datetime
    created_at: datetime
    

    model_config = {"from_attributes": True}