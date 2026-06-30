from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models.fleet import Truck, Trailer, Load, Incident, TruckStatus, LoadStatus, LoadPriority, TrailerType, IncidentType, IncidentSeverity
from app.models.user import User
from app.api.dependencies.auth import get_current_user

router = APIRouter(tags=["Fleet"])


# ─── Pydantic schemas inline (will move to schemas/ on Day 2+) ───────────────

class TruckOut(BaseModel):
    id: str
    unit_number: str
    make: str
    model: str
    year: int
    status: TruckStatus
    odometer: int
    assigned_driver_id: Optional[str]
    next_service_miles: int
    model_config = {"from_attributes": True}


class TrailerOut(BaseModel):
    id: str
    unit_number: str
    trailer_type: TrailerType
    length_ft: int
    capacity_lbs: int
    status: TruckStatus
    assigned_driver_id: Optional[str]
    model_config = {"from_attributes": True}


class LoadOut(BaseModel):
    id: str
    load_number: str
    origin_city: str
    origin_state: str
    dest_city: str
    dest_state: str
    pickup_appointment: datetime
    delivery_appointment: datetime
    commodity: str
    weight_lbs: int
    status: LoadStatus
    priority: LoadPriority
    assigned_driver_id: Optional[str]
    assigned_truck_id: Optional[str]
    customer_name: str
    rate_usd: float
    estimated_miles: int
    model_config = {"from_attributes": True}


class LoadAssign(BaseModel):
    driver_id: str
    truck_id: Optional[str] = None
    trailer_id: Optional[str] = None


class IncidentOut(BaseModel):
    id: str
    incident_number: str
    incident_type: IncidentType
    severity: IncidentSeverity
    title: str
    description: str
    driver_id: Optional[str]
    load_id: Optional[str]
    is_resolved: bool
    occurred_at: datetime
    ai_recommended_action: Optional[str]
    model_config = {"from_attributes": True}


class IncidentCreate(BaseModel):
    incident_type: IncidentType
    severity: IncidentSeverity
    title: str
    description: str
    location: Optional[str] = None
    driver_id: Optional[str] = None
    load_id: Optional[str] = None
    truck_id: Optional[str] = None


# ─── Trucks ──────────────────────────────────────────────────────────────────

@router.get("/trucks", response_model=list[TruckOut])
async def list_trucks(
    status: Optional[TruckStatus] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(Truck).where(Truck.is_active == True)
    if status:
        q = q.where(Truck.status == status)
    result = await db.execute(q.order_by(Truck.unit_number))
    return result.scalars().all()


@router.get("/trucks/stats")
async def truck_stats(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    total = await db.scalar(select(func.count(Truck.id)).where(Truck.is_active == True))
    available = await db.scalar(select(func.count(Truck.id)).where(Truck.is_active == True, Truck.status == TruckStatus.AVAILABLE))
    maintenance = await db.scalar(select(func.count(Truck.id)).where(Truck.is_active == True, Truck.status == TruckStatus.MAINTENANCE))
    return {"total": total, "available": available, "in_maintenance": maintenance}


# ─── Trailers ─────────────────────────────────────────────────────────────────

@router.get("/trailers", response_model=list[TrailerOut])
async def list_trailers(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Trailer).where(Trailer.is_active == True).order_by(Trailer.unit_number))
    return result.scalars().all()


# ─── Loads ───────────────────────────────────────────────────────────────────

@router.get("/loads", response_model=list[LoadOut])
async def list_loads(
    status: Optional[LoadStatus] = None,
    priority: Optional[LoadPriority] = None,
    unassigned: bool = False,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(Load)
    if status:
        q = q.where(Load.status == status)
    if priority:
        q = q.where(Load.priority == priority)
    if unassigned:
        q = q.where(Load.assigned_driver_id == None, Load.status == LoadStatus.PENDING)
    result = await db.execute(q.order_by(Load.pickup_appointment))
    return result.scalars().all()


@router.get("/loads/{load_id}", response_model=LoadOut)
async def get_load(load_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(Load).where(Load.id == load_id))
    load = result.scalar_one_or_none()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    return load


@router.post("/loads/{load_id}/assign", response_model=LoadOut)
async def assign_load(
    load_id: str,
    payload: LoadAssign,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Load).where(Load.id == load_id))
    load = result.scalar_one_or_none()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")

    load.assigned_driver_id = payload.driver_id
    load.assigned_truck_id = payload.truck_id
    load.assigned_trailer_id = payload.trailer_id
    load.status = LoadStatus.ASSIGNED
    await db.flush()
    return load


@router.get("/loads/stats/summary")
async def load_stats(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    total = await db.scalar(select(func.count(Load.id)))
    pending = await db.scalar(select(func.count(Load.id)).where(Load.status == LoadStatus.PENDING))
    in_transit = await db.scalar(select(func.count(Load.id)).where(Load.status == LoadStatus.IN_TRANSIT))
    delivered = await db.scalar(select(func.count(Load.id)).where(Load.status == LoadStatus.DELIVERED))
    return {"total": total, "pending": pending, "in_transit": in_transit, "delivered": delivered}


# ─── Incidents ───────────────────────────────────────────────────────────────

@router.get("/incidents", response_model=list[IncidentOut])
async def list_incidents(
    is_resolved: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(Incident)
    if is_resolved is not None:
        q = q.where(Incident.is_resolved == is_resolved)
    result = await db.execute(q.order_by(Incident.occurred_at.desc()))
    return result.scalars().all()


@router.post("/incidents", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
async def create_incident(
    payload: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    import uuid
    incident = Incident(
        incident_number=f"INC-{str(uuid.uuid4())[:8].upper()}",
        **payload.model_dump()
    )
    db.add(incident)
    await db.flush()
    return incident
