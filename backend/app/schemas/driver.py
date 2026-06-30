from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional
from app.models.driver import DriverStatus, DriverAvailability


class DriverCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    cdl_number: str
    cdl_expiry: date
    date_of_hire: date
    home_base: str


class DriverUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    current_location: Optional[str] = None
    status: Optional[DriverStatus] = None
    availability: Optional[DriverAvailability] = None
    hos_drive_remaining: Optional[float] = None
    hos_duty_remaining: Optional[float] = None
    notes: Optional[str] = None


class DriverOut(BaseModel):
    id: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: str
    cdl_number: str
    cdl_expiry: date
    date_of_hire: date
    home_base: str
    current_location: Optional[str]
    status: DriverStatus
    availability: DriverAvailability
    hos_drive_remaining: float
    hos_duty_remaining: float
    hos_cycle_remaining: float
    hos_violations: int
    on_time_delivery_rate: float
    safety_score: float
    detention_hours_mtd: float
    assigned_truck_id: Optional[str]
    assigned_trailer_id: Optional[str]
    current_load_id: Optional[str]
    notes: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DriverListOut(BaseModel):
    id: str
    full_name: str
    status: DriverStatus
    availability: DriverAvailability
    current_location: Optional[str]
    home_base: str
    hos_drive_remaining: float
    hos_duty_remaining: float
    on_time_delivery_rate: float
    safety_score: float
    current_load_id: Optional[str]

    model_config = {"from_attributes": True}
