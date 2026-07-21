"""
Trailer Pydantic schemas.

Three distinct shapes:
- TrailerCreate  : what the client sends to create a trailer
- TrailerUpdate  : partial update (all fields optional)
- TrailerResponse: what the API returns (includes DB-generated fields)
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.trailer import TrailerStatus, TrailerType


class TrailerCreate(BaseModel):
    trailer_number: str = Field(..., min_length=1, max_length=30, examples=["TR-2001"])
    trailer_type: TrailerType
    length_ft: int = Field(..., gt=0, le=60, examples=[53])
    capacity_lbs: int = Field(..., gt=0, le=50000, examples=[44000])
    status: TrailerStatus = TrailerStatus.AVAILABLE
    assigned_driver_id: Optional[str] = None
    assigned_truck_id: Optional[str] = None
    current_location: Optional[str] = Field(None, max_length=200)
    last_inspection_date: Optional[datetime] = None
    next_inspection_due: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("trailer_number")
    @classmethod
    def trailer_number_uppercase(cls, v: str) -> str:
        return v.strip().upper()


class TrailerUpdate(BaseModel):
    """All fields optional — only provided fields are updated."""
    trailer_type: Optional[TrailerType] = None
    length_ft: Optional[int] = Field(None, gt=0, le=60)
    capacity_lbs: Optional[int] = Field(None, gt=0, le=50000)
    status: Optional[TrailerStatus] = None
    assigned_driver_id: Optional[str] = None
    assigned_truck_id: Optional[str] = None
    current_location: Optional[str] = Field(None, max_length=200)
    last_inspection_date: Optional[datetime] = None
    next_inspection_due: Optional[datetime] = None
    notes: Optional[str] = None


class TrailerResponse(BaseModel):
    id: str
    trailer_number: str
    trailer_type: TrailerType
    length_ft: int
    capacity_lbs: int
    status: TrailerStatus
    assigned_driver_id: Optional[str]
    assigned_truck_id: Optional[str]
    current_location: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}