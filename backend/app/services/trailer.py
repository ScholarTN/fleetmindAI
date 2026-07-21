"""
Trailer service.

Responsibility: business logic and orchestration.
Never writes SQL. Always goes through TrailerRepository.
Routes call this; the repository is an implementation detail.
"""
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trailer import Trailer, TrailerStatus, TrailerType
from app.repositories.trailer import TrailerRepository
from app.schemas.trailer import TrailerCreate, TrailerUpdate


class TrailerService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = TrailerRepository(db)

    # ── Queries ───────────────────────────────────────────────────────────────

    async def get_trailer(self, trailer_id: str) -> Trailer:
        """Fetch a single trailer or raise 404."""
        trailer = await self._repo.get_by_id(trailer_id)
        if not trailer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trailer '{trailer_id}' not found.",
            )
        return trailer

    async def list_trailers(
        self,
        status: Optional[TrailerStatus] = None,
        trailer_type: Optional[TrailerType] = None,
        assigned_driver_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Trailer]:
        return await self._repo.list_all(
            status=status,
            trailer_type=trailer_type,
            assigned_driver_id=assigned_driver_id,
            limit=limit,
            offset=offset,
        )

    async def get_stats(self) -> dict:
        """Fleet-level trailer counts by status."""
        total = await self._repo.count()
        available = await self._repo.count_by_status(TrailerStatus.AVAILABLE)
        in_use = await self._repo.count_by_status(TrailerStatus.IN_USE)
        maintenance = await self._repo.count_by_status(TrailerStatus.MAINTENANCE)
        return {
            "total": total,
            "available": available,
            "in_use": in_use,
            "in_maintenance": maintenance,
        }

    # ── Commands ──────────────────────────────────────────────────────────────

    async def create_trailer(self, payload: TrailerCreate) -> Trailer:
        """
        Create a new trailer.
        Enforces: trailer_number must be unique across the fleet.
        """
        existing = await self._repo.get_by_trailer_number(payload.trailer_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Trailer number '{payload.trailer_number}' is already in use.",
            )

        trailer = Trailer(**payload.model_dump(exclude={"last_inspection_date", "next_inspection_due"}))
        return await self._repo.create(trailer)

    async def update_trailer(self, trailer_id: str, payload: TrailerUpdate) -> Trailer:
        """
        Partial update. Only fields included in the request body are changed.
        """
        trailer = await self.get_trailer(trailer_id)
        changes = payload.model_dump(exclude_none=True)
        if not changes:
            return trailer
        return await self._repo.update(trailer, changes)

    async def assign_driver(self, trailer_id: str, driver_id: Optional[str]) -> Trailer:
        """
        Assign or unassign a driver from a trailer.
        Passing None clears the assignment.
        """
        trailer = await self.get_trailer(trailer_id)

        # Business rule: cannot assign a driver to an out-of-service trailer
        if driver_id and trailer.status == TrailerStatus.OUT_OF_SERVICE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign a driver to a trailer that is out of service.",
            )

        changes = {"assigned_driver_id": driver_id}
        if driver_id:
            changes["status"] = TrailerStatus.IN_USE
        else:
            # Unassigning — only reset to available if no truck is still attached
            if not trailer.assigned_truck_id:
                changes["status"] = TrailerStatus.AVAILABLE

        return await self._repo.update(trailer, changes)

    async def assign_truck(self, trailer_id: str, truck_id: Optional[str]) -> Trailer:
        """
        Assign or unassign a truck from a trailer.
        Passing None clears the truck assignment.
        """
        trailer = await self.get_trailer(trailer_id)

        if truck_id and trailer.status == TrailerStatus.OUT_OF_SERVICE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign a truck to a trailer that is out of service.",
            )

        changes = {"assigned_truck_id": truck_id}
        return await self._repo.update(trailer, changes)

    async def update_status(self, trailer_id: str, new_status: TrailerStatus) -> Trailer:
        """
        Change trailer operational status.
        Business rule: cannot mark as available if a driver is assigned.
        """
        trailer = await self.get_trailer(trailer_id)

        if new_status == TrailerStatus.AVAILABLE and trailer.assigned_driver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot mark trailer as available while a driver is assigned. "
                       "Unassign the driver first.",
            )

        return await self._repo.update(trailer, {"status": new_status})

    async def delete_trailer(self, trailer_id: str) -> None:
        """
        Delete a trailer.
        Business rule: cannot delete a trailer currently in use.
        """
        trailer = await self.get_trailer(trailer_id)

        if trailer.status == TrailerStatus.IN_USE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete a trailer that is currently in use. "
                       "Unassign it first.",
            )

        await self._repo.delete(trailer)