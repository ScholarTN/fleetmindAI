from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.truck import Truck, TruckStatus


class TruckRepository:
    async def create(
        self,
        db: AsyncSession,
        truck: Truck,
    ) -> Truck:
        db.add(truck)
        await db.commit()
        await db.refresh(truck)
        return truck

    async def get_by_id(
        self,
        db: AsyncSession,
        truck_id: str,
    ) -> Truck | None:
        result = await db.execute(
            select(Truck).where(
                Truck.id == truck_id,
                Truck.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list_active(
        self,
        db: AsyncSession,
    ) -> list[Truck]:
        result = await db.execute(
            select(Truck).where(
                Truck.is_active.is_(True)
            )
        )
        return result.scalars().all()

    async def get_by_truck_number(
        self,
        db: AsyncSession,
        truck_number: str,
    ) -> Truck | None:
        result = await db.execute(
            select(Truck).where(
                Truck.truck_number == truck_number,
                Truck.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_vin(
        self,
        db: AsyncSession,
        vin: str,
    ) -> Truck | None:
        result = await db.execute(
            select(Truck).where(
                Truck.vin == vin,
                Truck.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_license_plate(
        self,
        db: AsyncSession,
        plate: str,
    ) -> Truck | None:
        result = await db.execute(
            select(Truck).where(
                Truck.license_plate == plate,
                Truck.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list_available(
        self,
        db: AsyncSession,
    ) -> list[Truck]:
        result = await db.execute(
            select(Truck).where(
                Truck.status == TruckStatus.AVAILABLE,
                Truck.is_active.is_(True),
            )
        )
        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        truck: Truck,
    ) -> Truck:
        await db.commit()
        await db.refresh(truck)
        return truck

    async def delete(
        self,
        db: AsyncSession,
        truck: Truck,
    ) -> Truck:
        truck.is_active = False
        await db.commit()
        await db.refresh(truck)
        return truck


truck_repository = TruckRepository()