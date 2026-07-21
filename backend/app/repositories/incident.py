from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident import Incident, IncidentType, IncidentSeverity


class IncidentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, incident_id: str) -> Optional[Incident]:
        result = await self._db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        return result.scalar_one_or_none()

    async def get_by_incident_number(self, incident_number: str) -> Optional[Incident]:
        result = await self._db.execute(
            select(Incident).where(Incident.incident_number == incident_number)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        is_resolved: Optional[bool] = None,
        severity: Optional[IncidentSeverity] = None,
        incident_type: Optional[IncidentType] = None,
        driver_id: Optional[str] = None,
        load_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Incident]:
        q = select(Incident)
        if is_resolved is not None:
            q = q.where(Incident.is_resolved == is_resolved)
        if severity:
            q = q.where(Incident.severity == severity)
        if incident_type:
            q = q.where(Incident.incident_type == incident_type)
        if driver_id:
            q = q.where(Incident.driver_id == driver_id)
        if load_id:
            q = q.where(Incident.load_id == load_id)
        q = q.order_by(Incident.occurred_at.desc()).offset(offset).limit(limit)
        result = await self._db.execute(q)
        return result.scalars().all()

    async def count_by_severity(self, severity: IncidentSeverity) -> int:
        result = await self._db.execute(
            select(func.count(Incident.id)).where(
                Incident.severity == severity,
                Incident.is_resolved == False,
            )
        )
        return result.scalar_one()

    async def create(self, incident: Incident) -> Incident:
        self._db.add(incident)
        await self._db.flush()
        await self._db.refresh(incident)
        return incident

    async def update(self, incident: Incident, changes: dict) -> Incident:
        for field, value in changes.items():
            setattr(incident, field, value)
        await self._db.flush()
        await self._db.refresh(incident)
        return incident