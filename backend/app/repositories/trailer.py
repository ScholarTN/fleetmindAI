"""
Trailer repository.

Responsibility: database access only.
No business logic. No HTTP concerns.
Services call this; routes never call this directly.
"""
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trailer import Trailer, TrailerStatus, TrailerType


class TrailerRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Reads ─────────────────────────────────────────────────────────────────

    async def get_by_id(self, trailer_id: str) -> Optional[Trailer]:
        result = await self._db.execute(
            select(Trailer).where(Trailer.id == trailer_id)
        )
        return result.scalar_one_or_none()

    async def get_by_trailer_number(self, trailer_number: str) -> Optional[Trailer]:
        result = await self._db.execute(
            select(Trailer).where(Trailer.trailer_number == trailer_number)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        status: Optional[TrailerStatus] = None,
        trailer_type: Optional[TrailerType] = None,
        assigned_driver_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Trailer]:
        q = select(Trailer)
        if status:
            q = q.where(Trailer.status == status)
        if trailer_type:
            q = q.where(Trailer.trailer_type == trailer_type)
        if assigned_driver_id:
            q = q.where(Trailer.assigned_driver_id == assigned_driver_id)
        q = q.order_by(Trailer.trailer_number).offset(offset).limit(limit)
        result = await self._db.execute(q)
        return result.scalars().all()

    async def count(self) -> int:
        result = await self._db.execute(select(func.count(Trailer.id)))
        return result.scalar_one()

    async def count_by_status(self, status: TrailerStatus) -> int:
        result = await self._db.execute(
            select(func.count(Trailer.id)).where(Trailer.status == status)
        )
        return result.scalar_one()

    # ── Writes ────────────────────────────────────────────────────────────────

    async def create(self, trailer: Trailer) -> Trailer:
        self._db.add(trailer)
        await self._db.flush()
        await self._db.refresh(trailer)
        return trailer

    async def update(self, trailer: Trailer, changes: dict) -> Trailer:
        for field, value in changes.items():
            setattr(trailer, field, value)
        await self._db.flush()
        await self._db.refresh(trailer)
        return trailer

    async def delete(self, trailer: Trailer) -> None:
        await self._db.delete(trailer)
        await self._db.flush()