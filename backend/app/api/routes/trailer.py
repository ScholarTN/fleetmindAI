"""
Trailer routes.

Thin HTTP layer only.
No business logic. No database access.
All work is delegated to TrailerService.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.trailer import TrailerStatus, TrailerType
from app.schemas.trailer import TrailerCreate, TrailerResponse, TrailerUpdate
from app.services.trailer import TrailerService

# Auth dependency — import from your existing dependencies module
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/trailers", tags=["Trailers"])


def get_trailer_service(db: AsyncSession = Depends(get_db)) -> TrailerService:
    """Dependency that provides a TrailerService bound to the current DB session."""
    return TrailerService(db)


# ── Collection endpoints ──────────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[TrailerResponse],
    summary="List trailers",
)
async def list_trailers(
    status: Optional[TrailerStatus] = Query(None, description="Filter by operational status"),
    trailer_type: Optional[TrailerType] = Query(None, description="Filter by trailer type"),
    assigned_driver_id: Optional[str] = Query(None, description="Filter by assigned driver"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: TrailerService = Depends(get_trailer_service),
    _=Depends(get_current_user),
):
    return await service.list_trailers(
        status=status,
        trailer_type=trailer_type,
        assigned_driver_id=assigned_driver_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/stats",
    summary="Fleet-level trailer statistics",
)
async def trailer_stats(
    service: TrailerService = Depends(get_trailer_service),
    _=Depends(get_current_user),
):
    return await service.get_stats()


@router.post(
    "",
    response_model=TrailerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trailer",
)
async def create_trailer(
    payload: TrailerCreate,
    service: TrailerService = Depends(get_trailer_service),
    _=Depends(get_current_user),
):
    return await service.create_trailer(payload)


# ── Item endpoints ────────────────────────────────────────────────────────────

@router.get(
    "/{trailer_id}",
    response_model=TrailerResponse,
    summary="Get a single trailer",
)
async def get_trailer(
    trailer_id: str,
    service: TrailerService = Depends(get_trailer_service),
    _=Depends(get_current_user),
):
    return await service.get_trailer(trailer_id)


@router.patch(
    "/{trailer_id}",
    response_model=TrailerResponse,
    summary="Partially update a trailer",
)
async def update_trailer(
    trailer_id: str,
    payload: TrailerUpdate,
    service: TrailerService = Depends(get_trailer_service),
    _=Depends(get_current_user),
):
    return await service.update_trailer(trailer_id, payload)


@router.patch(
    "/{trailer_id}/status",
    response_model=TrailerResponse,
    summary="Update trailer operational status",
)
async def update_status(
    trailer_id: str,
    new_status: TrailerStatus = Query(..., description="New status to apply"),
    service: TrailerService = Depends(get_trailer_service),
    _=Depends(get_current_user),
):
    return await service.update_status(trailer_id, new_status)


@router.patch(
    "/{trailer_id}/assign-driver",
    response_model=TrailerResponse,
    summary="Assign or unassign a driver",
)
async def assign_driver(
    trailer_id: str,
    driver_id: Optional[str] = Query(None, description="Driver ID to assign, or null to unassign"),
    service: TrailerService = Depends(get_trailer_service),
    _=Depends(get_current_user),
):
    return await service.assign_driver(trailer_id, driver_id)


@router.patch(
    "/{trailer_id}/assign-truck",
    response_model=TrailerResponse,
    summary="Assign or unassign a truck",
)
async def assign_truck(
    trailer_id: str,
    truck_id: Optional[str] = Query(None, description="Truck ID to assign, or null to unassign"),
    service: TrailerService = Depends(get_trailer_service),
    _=Depends(get_current_user),
):
    return await service.assign_truck(trailer_id, truck_id)


@router.delete(
    "/{trailer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a trailer",
)
async def delete_trailer(
    trailer_id: str,
    service: TrailerService = Depends(get_trailer_service),
    _=Depends(get_current_user),
):
    await service.delete_trailer(trailer_id)