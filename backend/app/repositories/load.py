from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.load import Load, LoadStatus, LoadPriority


class LoadRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, load_id: str) -> Optional[Load]:
        result = await self._db.execute(
            select(Load).where(Load.id == load_id)
        )
        return result.scalar_one_or_none()

    async def get_by_load_number(self, load_number: str) -> Optional[Load]:
        result = await self._db.execute(
            select(Load).where(Load.load_number == load_number)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        status: Optional[LoadStatus] = None,
        priority: Optional[LoadPriority] = None,
        assigned_driver_id: Optional[str] = None,
        unassigned: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Load]:
        q = select(Load)
        if status:
            q = q.where(Load.status == status)
        if priority:
            q = q.where(Load.priority == priority)
        if assigned_driver_id:
            q = q.where(Load.assigned_driver_id == assigned_driver_id)
        if unassigned:
            q = q.where(
                Load.assigned_driver_id == None,
                Load.status == LoadStatus.PENDING
            )
        q = q.order_by(Load.pickup_appointment).offset(offset).limit(limit)
        result = await self._db.execute(q)
        return result.scalars().all()

    async def count_by_status(self, status: LoadStatus) -> int:
        result = await self._db.execute(
            select(func.count(Load.id)).where(Load.status == status)
        )
        return result.scalar_one()

    async def create(self, load: Load) -> Load:
        self._db.add(load)
        await self._db.flush()
        await self._db.refresh(load)
        return load

    async def update(self, load: Load, changes: dict) -> Load:
        for field, value in changes.items():
            setattr(load, field, value)
        await self._db.flush()
        await self._db.refresh(load)
        return load