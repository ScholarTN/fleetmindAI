from typing import Optional, Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.load import Load, LoadStatus
from app.repositories.load import LoadRepository
from app.schemas.load import LoadCreate, LoadUpdate, LoadAssign


class LoadService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = LoadRepository(db)

    async def get_load(self, load_id: str) -> Load:
        load = await self._repo.get_by_id(load_id)
        if not load:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Load '{load_id}' not found.",
            )
        return load

    async def list_loads(
        self,
        status: Optional[LoadStatus] = None,
        priority=None,
        assigned_driver_id: Optional[str] = None,
        unassigned: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Load]:
        return await self._repo.list_all(
            status=status,
            priority=priority,
            assigned_driver_id=assigned_driver_id,
            unassigned=unassigned,
            limit=limit,
            offset=offset,
        )

    async def get_stats(self) -> dict:
        pending = await self._repo.count_by_status(LoadStatus.PENDING)
        assigned = await self._repo.count_by_status(LoadStatus.ASSIGNED)
        in_transit = await self._repo.count_by_status(LoadStatus.IN_TRANSIT)
        delivered = await self._repo.count_by_status(LoadStatus.DELIVERED)
        return {
            "pending": pending,
            "assigned": assigned,
            "in_transit": in_transit,
            "delivered": delivered,
            "total": pending + assigned + in_transit + delivered,
        }

    async def create_load(self, payload: LoadCreate) -> Load:
        existing = await self._repo.get_by_load_number(payload.load_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Load number '{payload.load_number}' already exists.",
            )
        if payload.delivery_appointment <= payload.pickup_appointment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery appointment must be after pickup appointment.",
            )
        load = Load(**payload.model_dump())
        return await self._repo.create(load)

    async def update_load(self, load_id: str, payload: LoadUpdate) -> Load:
        load = await self.get_load(load_id)
        changes = payload.model_dump(exclude_none=True)
        if not changes:
            return load
        return await self._repo.update(load, changes)

    async def assign_load(self, load_id: str, payload: LoadAssign) -> Load:
        load = await self.get_load(load_id)
        if load.status == LoadStatus.DELIVERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign a delivered load.",
            )
        if load.status == LoadStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign a cancelled load.",
            )
        changes = {
            "assigned_driver_id": payload.driver_id,
            "assigned_truck_id": payload.truck_id,
            "assigned_trailer_id": payload.trailer_id,
            "status": LoadStatus.ASSIGNED,
        }
        return await self._repo.update(load, changes)

    async def update_status(self, load_id: str, new_status: LoadStatus) -> Load:
        load = await self.get_load(load_id)
        if load.status == LoadStatus.DELIVERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status of a delivered load.",
            )
        return await self._repo.update(load, {"status": new_status})