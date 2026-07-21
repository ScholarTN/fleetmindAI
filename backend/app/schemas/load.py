from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.load import LoadStatus, LoadPriority
from app.models.trailer import TrailerType


class LoadCreate(BaseModel):
    load_number: str = Field(..., min_length=1, max_length=30)
    origin_city: str
    origin_state: str = Field(..., min_length=2, max_length=2)
    origin_address: Optional[str] = None
    dest_city: str
    dest_state: str = Field(..., min_length=2, max_length=2)
    dest_address: Optional[str] = None
    estimated_miles: int = Field(default=0, ge=0)
    pickup_appointment: datetime
    delivery_appointment: datetime
    commodity: str
    weight_lbs: int = Field(default=0, ge=0)
    trailer_type_required: TrailerType = TrailerType.DRY_VAN
    priority: LoadPriority = LoadPriority.NORMAL
    customer_name: str
    customer_reference: Optional[str] = None
    rate_usd: float = Field(default=0.0, ge=0)
    notes: Optional[str] = None


class LoadUpdate(BaseModel):
    origin_city: Optional[str] = None
    origin_state: Optional[str] = None
    origin_address: Optional[str] = None
    dest_city: Optional[str] = None
    dest_state: Optional[str] = None
    dest_address: Optional[str] = None
    estimated_miles: Optional[int] = None
    pickup_appointment: Optional[datetime] = None
    delivery_appointment: Optional[datetime] = None
    commodity: Optional[str] = None
    weight_lbs: Optional[int] = None
    trailer_type_required: Optional[TrailerType] = None
    priority: Optional[LoadPriority] = None
    customer_name: Optional[str] = None
    customer_reference: Optional[str] = None
    rate_usd: Optional[float] = None
    notes: Optional[str] = None


class LoadAssign(BaseModel):
    driver_id: str
    truck_id: Optional[str] = None
    trailer_id: Optional[str] = None


class LoadResponse(BaseModel):
    id: str
    load_number: str
    origin_city: str
    origin_state: str
    origin_address: Optional[str]
    dest_city: str
    dest_state: str
    dest_address: Optional[str]
    estimated_miles: int
    pickup_appointment: datetime
    delivery_appointment: datetime
    pickup_actual: Optional[datetime]
    delivery_actual: Optional[datetime]
    commodity: str
    weight_lbs: int
    trailer_type_required: TrailerType
    status: LoadStatus
    priority: LoadPriority
    assigned_driver_id: Optional[str]
    assigned_truck_id: Optional[str]
    assigned_trailer_id: Optional[str]
    customer_name: str
    customer_reference: Optional[str]
    rate_usd: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}