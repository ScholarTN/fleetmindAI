from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver import Driver, DriverAvailability
from app.models.truck import Truck, TruckStatus
from app.models.trailer import Trailer, TrailerStatus
from app.models.load import Load, LoadStatus
from app.models.incident import Incident


class DatabaseTools:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ----------------------------
    # Drivers
    # ----------------------------

    async def get_available_drivers(self) -> list[Driver]:
        result = await self.db.execute(
            select(Driver).where(
                Driver.availability == DriverAvailability.AVAILABLE
            )
        )
        return result.scalars().all()

    async def get_driver(self, driver_id: str) -> Driver | None:
        result = await self.db.execute(
            select(Driver).where(
                Driver.id == driver_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all_drivers(self) -> list[Driver]:
        result = await self.db.execute(select(Driver))
        return result.scalars().all()

    # ----------------------------
    # Trucks
    # ----------------------------

    async def get_available_trucks(self) -> list[Truck]:
        result = await self.db.execute(
            select(Truck).where(
                Truck.status == TruckStatus.AVAILABLE
            )
        )
        return result.scalars().all()

    async def get_truck(self, truck_id: str) -> Truck | None:
        result = await self.db.execute(
            select(Truck).where(
                Truck.id == truck_id
            )
        )
        return result.scalar_one_or_none()

    # ----------------------------
    # Trailers
    # ----------------------------

    async def get_available_trailers(self) -> list[Trailer]:
        result = await self.db.execute(
            select(Trailer).where(
                Trailer.status == TrailerStatus.AVAILABLE
            )
        )
        return result.scalars().all()

    async def get_trailer(self, trailer_id: str) -> Trailer | None:
        result = await self.db.execute(
            select(Trailer).where(
                Trailer.id == trailer_id
            )
        )
        return result.scalar_one_or_none()

    # ----------------------------
    # Loads
    # ----------------------------

    async def get_load(self, load_id: str) -> Load | None:
        result = await self.db.execute(
            select(Load).where(
                Load.id == load_id
            )
        )
        return result.scalar_one_or_none()

    async def get_pending_loads(self) -> list[Load]:
        result = await self.db.execute(
            select(Load).where(
                Load.status == LoadStatus.PENDING
            )
        )
        return result.scalars().all()

    async def get_active_loads(self) -> list[Load]:
        result = await self.db.execute(
            select(Load).where(
                Load.status.in_(
                    [
                        LoadStatus.ASSIGNED,
                        LoadStatus.IN_TRANSIT,
                        LoadStatus.AT_PICKUP,
                        LoadStatus.LOADED,
                        LoadStatus.AT_DELIVERY,
                    ]
                )
            )
        )
        return result.scalars().all()

    # ----------------------------
    # Incidents
    # ----------------------------

    async def get_recent_incidents(
        self,
        limit: int = 10,
    ) -> list[Incident]:
        result = await self.db.execute(
            select(Incident)
            .order_by(Incident.occurred_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_driver_incidents(
        self,
        driver_id: str,
    ) -> list[Incident]:
        result = await self.db.execute(
            select(Incident).where(
                Incident.driver_id == driver_id
            )
        )
        return result.scalars().all()