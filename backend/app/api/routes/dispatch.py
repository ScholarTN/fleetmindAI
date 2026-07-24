from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.services.dispatch import DispatchService
from app.schemas.load import LoadResponse
from app.schemas.driver import DriverListOut
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/dispatch", tags=["Dispatch"])


class DispatchAssign(BaseModel):
    load_id: str
    driver_id: str
    truck_id: Optional[str] = None
    trailer_id: Optional[str] = None


def get_dispatch_service(db: AsyncSession = Depends(get_db)) -> DispatchService:
    return DispatchService(db)


@router.post("/assign", response_model=LoadResponse)
async def assign_load(
    payload: DispatchAssign,
    service: DispatchService = Depends(get_dispatch_service),
    _=Depends(get_current_user),
):
    return await service.assign(
        load_id=payload.load_id,
        driver_id=payload.driver_id,
        truck_id=payload.truck_id,
        trailer_id=payload.trailer_id,
    )


@router.post("/unassign/{load_id}", response_model=LoadResponse)
async def unassign_load(
    load_id: str,
    service: DispatchService = Depends(get_dispatch_service),
    _=Depends(get_current_user),
):
    return await service.unassign(load_id)


@router.get("/available-drivers", response_model=list[DriverListOut])
async def available_drivers(
    service: DispatchService = Depends(get_dispatch_service),
    _=Depends(get_current_user),
):
    return await service.get_available_drivers()


@router.get("/unassigned-loads", response_model=list[LoadResponse])
async def unassigned_loads(
    service: DispatchService = Depends(get_dispatch_service),
    _=Depends(get_current_user),
):
    return await service.get_unassigned_loads()