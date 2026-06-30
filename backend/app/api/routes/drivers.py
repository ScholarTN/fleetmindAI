from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models.driver import Driver, DriverStatus, DriverAvailability
from app.models.user import User
from app.schemas.driver import DriverCreate, DriverUpdate, DriverOut, DriverListOut
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("", response_model=list[DriverListOut])
async def list_drivers(
    status: Optional[DriverStatus] = None,
    availability: Optional[DriverAvailability] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(Driver).where(Driver.is_active == True)
    if status:
        q = q.where(Driver.status == status)
    if availability:
        q = q.where(Driver.availability == availability)
    if search:
        term = f"%{search}%"
        q = q.where(
            Driver.first_name.ilike(term) |
            Driver.last_name.ilike(term) |
            Driver.current_location.ilike(term)
        )
    q = q.offset(offset).limit(limit).order_by(Driver.last_name)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/stats")
async def driver_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    total = await db.scalar(select(func.count(Driver.id)).where(Driver.is_active == True))
    available = await db.scalar(
        select(func.count(Driver.id)).where(
            Driver.is_active == True,
            Driver.availability == DriverAvailability.AVAILABLE
        )
    )
    on_duty = await db.scalar(
        select(func.count(Driver.id)).where(
            Driver.is_active == True,
            Driver.status == DriverStatus.DRIVING
        )
    )
    return {"total": total, "available": available, "on_duty": on_duty}


@router.get("/{driver_id}", response_model=DriverOut)
async def get_driver(
    driver_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.post("", response_model=DriverOut, status_code=status.HTTP_201_CREATED)
async def create_driver(
    payload: DriverCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    driver = Driver(**payload.model_dump())
    db.add(driver)
    await db.flush()
    return driver


@router.patch("/{driver_id}", response_model=DriverOut)
async def update_driver(
    driver_id: str,
    payload: DriverUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(driver, field, value)
    await db.flush()
    return driver


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(
    driver_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.is_active = False
    await db.flush()
