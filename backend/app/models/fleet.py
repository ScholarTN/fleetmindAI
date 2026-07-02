import enum
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Boolean, Enum, DateTime, Float, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base



class TruckStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class TrailerType(str, enum.Enum):
    DRY_VAN = "dry_van"
    REEFER = "reefer"
    FLATBED = "flatbed"
    STEP_DECK = "step_deck"
    TANKER = "tanker"
    LOWBOY = "lowboy"


class LoadStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    AT_PICKUP = "at_pickup"
    LOADED = "loaded"
    AT_DELIVERY = "at_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class LoadPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentType(str, enum.Enum):
    BREAKDOWN = "breakdown"
    ACCIDENT = "accident"
    WEATHER_DELAY = "weather_delay"
    TRAFFIC_DELAY = "traffic_delay"
    FLAT_TIRE = "flat_tire"
    FUEL_ISSUE = "fuel_issue"
    DOT_INSPECTION = "dot_inspection"
    CUSTOMER_DELAY = "customer_delay"
    DETENTION = "detention"
    ROAD_CLOSURE = "road_closure"
    DRIVER_ILLNESS = "driver_illness"
    CARGO_ISSUE = "cargo_issue"
    OTHER = "other"


class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ─── Truck ───────────────────────────────────────────────────────────────────

class Truck(Base):
    __tablename__ = "trucks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    make: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    vin: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    license_plate: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[TruckStatus] = mapped_column(Enum(TruckStatus), default=TruckStatus.AVAILABLE)
    odometer: Mapped[int] = mapped_column(Integer, default=0)
    last_service_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_service_miles: Mapped[int] = mapped_column(Integer, default=0)
    assigned_driver_id: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


# ─── Trailer ─────────────────────────────────────────────────────────────────

class Trailer(Base):
    __tablename__ = "trailers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    trailer_type: Mapped[TrailerType] = mapped_column(Enum(TrailerType), nullable=False)
    length_ft: Mapped[int] = mapped_column(Integer, default=53)
    capacity_lbs: Mapped[int] = mapped_column(Integer, default=44000)
    status: Mapped[TruckStatus] = mapped_column(Enum(TruckStatus), default=TruckStatus.AVAILABLE)
    assigned_driver_id: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


# ─── Load ────────────────────────────────────────────────────────────────────

class Load(Base):
    __tablename__ = "loads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    load_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    # Route
    origin_city: Mapped[str] = mapped_column(String(100), nullable=False)
    origin_state: Mapped[str] = mapped_column(String(2), nullable=False)
    origin_address: Mapped[str] = mapped_column(String(255), nullable=True)
    dest_city: Mapped[str] = mapped_column(String(100), nullable=False)
    dest_state: Mapped[str] = mapped_column(String(2), nullable=False)
    dest_address: Mapped[str] = mapped_column(String(255), nullable=True)
    estimated_miles: Mapped[int] = mapped_column(Integer, default=0)

    # Appointments
    pickup_appointment: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivery_appointment: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    pickup_actual: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_actual: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Cargo
    commodity: Mapped[str] = mapped_column(String(100), nullable=False)
    weight_lbs: Mapped[int] = mapped_column(Integer, default=0)
    trailer_type_required: Mapped[TrailerType] = mapped_column(
        Enum(TrailerType), default=TrailerType.DRY_VAN
    )

    # Status
    status: Mapped[LoadStatus] = mapped_column(Enum(LoadStatus), default=LoadStatus.PENDING)
    priority: Mapped[LoadPriority] = mapped_column(Enum(LoadPriority), default=LoadPriority.NORMAL)

    # Assignment
    assigned_driver_id: Mapped[str | None] = mapped_column(String, nullable=True)
    assigned_truck_id: Mapped[str | None] = mapped_column(String, nullable=True)
    assigned_trailer_id: Mapped[str | None] = mapped_column(String, nullable=True)

    # Customer
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_reference: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Financials
    rate_usd: Mapped[float] = mapped_column(Float, default=0.0)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# ─── Incident ────────────────────────────────────────────────────────────────

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    incident_type: Mapped[IncidentType] = mapped_column(Enum(IncidentType), nullable=False)
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity), default=IncidentSeverity.MEDIUM
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Linked entities
    driver_id: Mapped[str | None] = mapped_column(String, nullable=True)
    load_id: Mapped[str | None] = mapped_column(String, nullable=True)
    truck_id: Mapped[str | None] = mapped_column(String, nullable=True)

    # AI-generated field (populated later)
    ai_recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
