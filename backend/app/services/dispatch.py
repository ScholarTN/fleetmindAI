from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.load import Load, LoadStatus
from app.models.driver import Driver, DriverAvailability
from app.models.truck import Truck, TruckStatus
from app.models.trailer import Trailer, TrailerStatus


class DispatchService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def assign(
        self,
        load_id: str,
        driver_id: str,
        truck_id: str | None = None,
        trailer_id: str | None = None,
    ) -> Load:
        # Get load
        result = await self._db.execute(select(Load).where(Load.id == load_id))
        load = result.scalar_one_or_none()
        if not load:
            raise HTTPException(status_code=404, detail="Load not found.")
        if load.status in (LoadStatus.DELIVERED, LoadStatus.CANCELLED):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot dispatch a {load.status} load.",
            )

        # Get driver
        result = await self._db.execute(select(Driver).where(Driver.id == driver_id))
        driver = result.scalar_one_or_none()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found.")
        if driver.availability == DriverAvailability.UNAVAILABLE:
            raise HTTPException(
                status_code=400,
                detail=f"Driver {driver.first_name} {driver.last_name} is unavailable.",
            )
        if driver.hos_drive_remaining < 1.0:
            raise HTTPException(
                status_code=400,
                detail=f"Driver {driver.first_name} {driver.last_name} has insufficient HOS remaining.",
            )

        # Get truck if provided
        if truck_id:
            result = await self._db.execute(select(Truck).where(Truck.id == truck_id))
            truck = result.scalar_one_or_none()
            if not truck:
                raise HTTPException(status_code=404, detail="Truck not found.")
            if truck.status == TruckStatus.OUT_OF_SERVICE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Truck {truck.truck_number} is out of service.",
                )

        # Get trailer if provided
        if trailer_id:
            result = await self._db.execute(
                select(Trailer).where(Trailer.id == trailer_id)
            )
            trailer = result.scalar_one_or_none()
            if not trailer:
                raise HTTPException(status_code=404, detail="Trailer not found.")
            if trailer.status == TrailerStatus.OUT_OF_SERVICE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Trailer {trailer.trailer_number} is out of service.",
                )

        # Execute dispatch
        load.assigned_driver_id = driver_id
        load.assigned_truck_id = truck_id
        load.assigned_trailer_id = trailer_id
        load.status = LoadStatus.ASSIGNED

        driver.availability = DriverAvailability.UNAVAILABLE
        driver.current_load_id = load_id

        await self._db.flush()
        await self._db.refresh(load)
        return load

    async def unassign(self, load_id: str) -> Load:
        result = await self._db.execute(select(Load).where(Load.id == load_id))
        load = result.scalar_one_or_none()
        if not load:
            raise HTTPException(status_code=404, detail="Load not found.")
        if load.status == LoadStatus.IN_TRANSIT:
            raise HTTPException(
                status_code=400,
                detail="Cannot unassign a load that is in transit.",
            )

        # Free the driver
        if load.assigned_driver_id:
            result = await self._db.execute(
                select(Driver).where(Driver.id == load.assigned_driver_id)
            )
            driver = result.scalar_one_or_none()
            if driver:
                driver.availability = DriverAvailability.AVAILABLE
                driver.current_load_id = None

        load.assigned_driver_id = None
        load.assigned_truck_id = None
        load.assigned_trailer_id = None
        load.status = LoadStatus.PENDING

        await self._db.flush()
        await self._db.refresh(load)
        return load

    async def get_available_drivers(self) -> list[Driver]:
        result = await self._db.execute(
            select(Driver).where(
                Driver.availability == DriverAvailability.AVAILABLE,
                Driver.hos_drive_remaining >= 1.0,
            )
        )
        return result.scalars().all()

    async def get_unassigned_loads(self) -> list[Load]:
        result = await self._db.execute(
            select(Load).where(
                Load.status == LoadStatus.PENDING,
                Load.assigned_driver_id == None,
            ).order_by(Load.pickup_appointment)
        )
        return result.scalars().all()