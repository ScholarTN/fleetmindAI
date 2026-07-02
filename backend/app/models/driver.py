import enum
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Boolean, Enum, DateTime, Float, Integer, Date, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base



class DriverStatus(str, enum.Enum):
    AVAILABLE = "available"
    ON_DUTY = "on_duty"
    DRIVING = "driving"
    OFF_DUTY = "off_duty"
    SLEEPER = "sleeper"
    YARD_MOVE = "yard_move"
    PERSONAL_CONVEYANCE = "personal_conveyance"


class DriverAvailability(str, enum.Enum):
    AVAILABLE = "available"
    LIMITED = "limited"       # < 4 hours HOS remaining
    UNAVAILABLE = "unavailable"
    HOME_TIME = "home_time"


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Personal info
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    cdl_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    cdl_expiry: Mapped[date] = mapped_column(Date, nullable=False)
    date_of_hire: Mapped[date] = mapped_column(Date, nullable=False)

    # Location
    home_base: Mapped[str] = mapped_column(String(100), nullable=False)
    current_location: Mapped[str] = mapped_column(String(200), nullable=True)
    current_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Status
    status: Mapped[DriverStatus] = mapped_column(
        Enum(DriverStatus), default=DriverStatus.OFF_DUTY
    )
    availability: Mapped[DriverAvailability] = mapped_column(
        Enum(DriverAvailability), default=DriverAvailability.AVAILABLE
    )

    # Hours of Service (HOS) - FMCSA property-carrying driver rules
    hos_drive_remaining: Mapped[float] = mapped_column(Float, default=11.0)   # 11-hour driving limit
    hos_duty_remaining: Mapped[float] = mapped_column(Float, default=14.0)    # 14-hour on-duty limit
    hos_cycle_remaining: Mapped[float] = mapped_column(Float, default=70.0)   # 70-hour/8-day cycle
    hos_last_reset: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hos_violations: Mapped[int] = mapped_column(Integer, default=0)

    # Performance metrics
    on_time_delivery_rate: Mapped[float] = mapped_column(Float, default=0.95)
    total_miles_ytd: Mapped[int] = mapped_column(Integer, default=0)
    safety_score: Mapped[float] = mapped_column(Float, default=100.0)
    detention_hours_mtd: Mapped[float] = mapped_column(Float, default=0.0)

    # Assignment
    assigned_truck_id: Mapped[str | None] = mapped_column(String, nullable=True)
    assigned_trailer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    current_load_id: Mapped[str | None] = mapped_column(String, nullable=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Driver {self.full_name} [{self.status}]>"
