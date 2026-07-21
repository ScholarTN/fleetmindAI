import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, Enum, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


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


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    incident_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    incident_type: Mapped[IncidentType] = mapped_column(
        Enum(IncidentType, name="incidenttype"), nullable=False
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="incidentseverity"),
        nullable=False,
        default=IncidentSeverity.MEDIUM,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    driver_id: Mapped[str | None] = mapped_column(String, nullable=True)
    load_id: Mapped[str | None] = mapped_column(String, nullable=True)
    truck_id: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
   