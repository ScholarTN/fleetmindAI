from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.load import LoadStatus, LoadPriority
from app.schemas.load import LoadCreate, LoadUpdate, LoadAssign, LoadResponse
from app.services.load import LoadService
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/loads", tags=["Loads"])


def get_load_service(db: AsyncSession = Depends(get_db)) -> LoadService:
    return LoadService(db)


@router.get("", response_model=list[LoadResponse])
async def list_loads(
    status: Optional[LoadStatus] = None,
    priority: Optional[LoadPriority] = None,
    assigned_driver_id: Optional[str] = None,
    unassigned: bool = False,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: LoadService = Depends(get_load_service),
    _=Depends(get_current_user),
):
    return await service.list_loads(
        status=status,
        priority=priority,
        assigned_driver_id=assigned_driver_id,
        unassigned=unassigned,
        limit=limit,
        offset=offset,
    )


@router.get("/stats")
async def load_stats(
    service: LoadService = Depends(get_load_service),
    _=Depends(get_current_user),
):
    return await service.get_stats()


@router.post("", response_model=LoadResponse, status_code=status.HTTP_201_CREATED)
async def create_load(
    payload: LoadCreate,
    service: LoadService = Depends(get_load_service),
    _=Depends(get_current_user),
):
    return await service.create_load(payload)


@router.get("/{load_id}", response_model=LoadResponse)
async def get_load(
    load_id: str,
    service: LoadService = Depends(get_load_service),
    _=Depends(get_current_user),
):
    return await service.get_load(load_id)


@router.patch("/{load_id}", response_model=LoadResponse)
async def update_load(
    load_id: str,
    payload: LoadUpdate,
    service: LoadService = Depends(get_load_service),
    _=Depends(get_current_user),
):
    return await service.update_load(load_id, payload)


@router.post("/{load_id}/assign", response_model=LoadResponse)
async def assign_load(
    load_id: str,
    payload: LoadAssign,
    service: LoadService = Depends(get_load_service),
    _=Depends(get_current_user),
):
    return await service.assign_load(load_id, payload)


@router.patch("/{load_id}/status", response_model=LoadResponse)
async def update_status(
    load_id: str,
    new_status: LoadStatus = Query(...),
    service: LoadService = Depends(get_load_service),
    _=Depends(get_current_user),
):
    return await service.update_status(load_id, new_status)