"""
Trailer model.

Follows the same SQLAlchemy 2.0 mapped_column() style as the Truck model.
One model only — no duplicates.
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, Enum, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TrailerType(str, enum.Enum):
    DRY_VAN = "dry_van"
    REEFER = "reefer"
    FLATBED = "flatbed"
    STEP_DECK = "step_deck"
    TANKER = "tanker"
    LOWBOY = "lowboy"


class TrailerStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class Trailer(Base):
    __tablename__ = "trailers"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    trailer_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    trailer_type: Mapped[TrailerType] = mapped_column(
        Enum(TrailerType, name="trailertype"), nullable=False
    )
    length_ft: Mapped[int] = mapped_column(Integer, nullable=False, default=53)
    capacity_lbs: Mapped[int] = mapped_column(Integer, nullable=False, default=44000)
    status: Mapped[TrailerStatus] = mapped_column(
        Enum(TrailerStatus, name="truckstatus"),
        nullable=False,
        default=TrailerStatus.AVAILABLE,
    )
    assigned_driver_id: Mapped[str | None] = mapped_column(String, nullable=True)
    assigned_truck_id: Mapped[str | None] = mapped_column(String, nullable=True)
    current_location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )