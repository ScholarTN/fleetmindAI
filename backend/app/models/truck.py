import enum
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TruckStatus(str, enum.Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class FuelType(str, enum.Enum):
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class Truck(Base):
    __tablename__ = "trucks"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # ==========================
    # Identity
    # ==========================

    truck_number: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    vin: Mapped[str] = mapped_column(
        String(17),
        unique=True,
        nullable=False,
    )

    license_plate: Mapped[str] = mapped_column(
        String(25),
        unique=True,
        nullable=False,
    )

    # ==========================
    # Vehicle Information
    # ==========================

    make: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    fuel_type: Mapped[FuelType] = mapped_column(
        Enum(FuelType),
        default=FuelType.DIESEL,
    )

    # ==========================
    # Operational Status
    # ==========================

    status: Mapped[TruckStatus] = mapped_column(
        Enum(TruckStatus),
        default=TruckStatus.AVAILABLE,
    )

    mileage: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    fuel_level: Mapped[float] = mapped_column(
        Float,
        default=100.0,
    )

    current_location: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    current_lat: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    current_lon: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # ==========================
    # Maintenance
    # ==========================

    last_service_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    next_service_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # ==========================
    # Future Relationships
    # ==========================

    assigned_driver_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    assigned_trailer_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    current_load_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    # ==========================
    # Miscellaneous
    # ==========================

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Truck {self.truck_number}>"