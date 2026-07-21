from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.incident import IncidentSeverity, IncidentType
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResolve,
    IncidentResponse,
)
from app.services.incident import IncidentService
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/incidents", tags=["Incidents"])


def get_incident_service(db: AsyncSession = Depends(get_db)) -> IncidentService:
    return IncidentService(db)


@router.get("", response_model=list[IncidentResponse])
async def list_incidents(
    is_resolved: Optional[bool] = None,
    severity: Optional[IncidentSeverity] = None,
    incident_type: Optional[IncidentType] = None,
    driver_id: Optional[str] = None,
    load_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: IncidentService = Depends(get_incident_service),
    _=Depends(get_current_user),
):
    return await service.list_incidents(
        is_resolved=is_resolved,
        severity=severity,
        incident_type=incident_type,
        driver_id=driver_id,
        load_id=load_id,
        limit=limit,
        offset=offset,
    )


@router.get("/stats")
async def incident_stats(
    service: IncidentService = Depends(get_incident_service),
    _=Depends(get_current_user),
):
    return await service.get_stats()


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    payload: IncidentCreate,
    service: IncidentService = Depends(get_incident_service),
    _=Depends(get_current_user),
):
    return await service.create_incident(payload)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    service: IncidentService = Depends(get_incident_service),
    _=Depends(get_current_user),
):
    return await service.get_incident(incident_id)


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    service: IncidentService = Depends(get_incident_service),
    _=Depends(get_current_user),
):
    return await service.update_incident(incident_id, payload)


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: str,
    payload: IncidentResolve,
    service: IncidentService = Depends(get_incident_service),
    _=Depends(get_current_user),
):
    return await service.resolve_incident(incident_id, payload)