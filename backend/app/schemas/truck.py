from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TruckStatus(str, Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class FuelType(str, Enum):
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


# -----------------------------
# Base Schema
# -----------------------------
class TruckBase(BaseModel):
    truck_number: str = Field(..., max_length=30)
    vin: str = Field(..., min_length=17, max_length=17)
    license_plate: str
    make: str
    model: str
    year: int = Field(..., ge=1980)
    fuel_type: FuelType = FuelType.DIESEL


# -----------------------------
# Create
# -----------------------------
class TruckCreate(TruckBase):
    pass


# -----------------------------
# Update
# -----------------------------
class TruckUpdate(BaseModel):
    truck_number: str | None = None
    vin: str | None = None
    license_plate: str | None = None
    make: str | None = None
    model: str | None = None
    year: int | None = None

    status: TruckStatus | None = None

    fuel_type: FuelType | None = None
    fuel_level: float | None = None

    mileage: int | None = None

    current_location: str | None = None
    current_lat: float | None = None
    current_lon: float | None = None

    last_service_date: date | None = None
    next_service_date: date | None = None

    assigned_driver_id: str | None = None
    assigned_trailer_id: str | None = None
    current_load_id: str | None = None

    notes: str | None = None

    is_active: bool | None = None


# -----------------------------
# Response
# -----------------------------
class TruckResponse(TruckBase):
    id: str

    status: TruckStatus

    mileage: int
    fuel_level: float

    current_location: str | None
    current_lat: float |None
    current_lon: float | None

    last_service_date: date | None
    next_service_date: date | None

    assigned_driver_id: str | None
    assigned_trailer_id: str | None
    current_load_id: str | None

    notes: str | None

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)