import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Enum, DateTime, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.trailer import TrailerType


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


class Load(Base):
    __tablename__ = "loads"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    load_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    origin_city: Mapped[str] = mapped_column(String(100), nullable=False)
    origin_state: Mapped[str] = mapped_column(String(2), nullable=False)
    origin_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dest_city: Mapped[str] = mapped_column(String(100), nullable=False)
    dest_state: Mapped[str] = mapped_column(String(2), nullable=False)
    dest_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estimated_miles: Mapped[int] = mapped_column(Integer, default=0)
    pickup_appointment: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    delivery_appointment: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    pickup_actual: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivery_actual: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    commodity: Mapped[str] = mapped_column(String(100), nullable=False)
    weight_lbs: Mapped[int] = mapped_column(Integer, default=0)
    trailer_type_required: Mapped[TrailerType] = mapped_column(
        Enum(TrailerType, name="trailertype"), default=TrailerType.DRY_VAN
    )
    status: Mapped[LoadStatus] = mapped_column(
        Enum(LoadStatus, name="loadstatus"), default=LoadStatus.PENDING
    )
    priority: Mapped[LoadPriority] = mapped_column(
        Enum(LoadPriority, name="loadpriority"), default=LoadPriority.NORMAL
    )
    assigned_driver_id: Mapped[str | None] = mapped_column(String, nullable=True)
    assigned_truck_id: Mapped[str | None] = mapped_column(String, nullable=True)
    assigned_trailer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_reference: Mapped[str | None] = mapped_column(String(50), nullable=True)
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