import uuid
from datetime import datetime, timezone
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident, IncidentSeverity, IncidentType
from app.repositories.incident import IncidentRepository
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResolve


class IncidentService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = IncidentRepository(db)

    def _generate_incident_number(self) -> str:
        return f"INC-{str(uuid.uuid4())[:8].upper()}"

    async def get_incident(self, incident_id: str) -> Incident:
        incident = await self._repo.get_by_id(incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident '{incident_id}' not found.",
            )
        return incident

    async def list_incidents(
        self,
        is_resolved: Optional[bool] = None,
        severity: Optional[IncidentSeverity] = None,
        incident_type: Optional[IncidentType] = None,
        driver_id: Optional[str] = None,
        load_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Incident]:
        return await self._repo.list_all(
            is_resolved=is_resolved,
            severity=severity,
            incident_type=incident_type,
            driver_id=driver_id,
            load_id=load_id,
            limit=limit,
            offset=offset,
        )

    async def get_stats(self) -> dict:
        critical = await self._repo.count_by_severity(IncidentSeverity.CRITICAL)
        high = await self._repo.count_by_severity(IncidentSeverity.HIGH)
        medium = await self._repo.count_by_severity(IncidentSeverity.MEDIUM)
        low = await self._repo.count_by_severity(IncidentSeverity.LOW)
        return {
            "open_critical": critical,
            "open_high": high,
            "open_medium": medium,
            "open_low": low,
            "total_open": critical + high + medium + low,
        }

    async def create_incident(self, payload: IncidentCreate) -> Incident:
        data = payload.model_dump(exclude_none=True)
        if "occurred_at" not in data:
            data["occurred_at"] = datetime.now(timezone.utc)
        incident = Incident(
            incident_number=self._generate_incident_number(),
            **data,
        )
        return await self._repo.create(incident)

    async def update_incident(
        self, incident_id: str, payload: IncidentUpdate
    ) -> Incident:
        incident = await self.get_incident(incident_id)
        if incident.is_resolved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update a resolved incident.",
            )
        changes = payload.model_dump(exclude_none=True)
        if not changes:
            return incident
        return await self._repo.update(incident, changes)

    async def resolve_incident(
        self, incident_id: str, payload: IncidentResolve
    ) -> Incident:
        incident = await self.get_incident(incident_id)
        if incident.is_resolved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incident is already resolved.",
            )
        changes = {
            "is_resolved": True,
            "resolved_at": datetime.now(timezone.utc),
            "resolution_notes": payload.resolution_notes,
        }
        return await self._repo.update(incident, changes)