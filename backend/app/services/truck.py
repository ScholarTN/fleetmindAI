from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.truck import Truck
from app.repositories.truck import truck_repository
from app.schemas.truck import TruckCreate, TruckUpdate


class TruckService:

    async def create_truck(
        self,
        db: AsyncSession,
        truck_data: TruckCreate,
    ) -> Truck:

        existing = await truck_repository.get_by_truck_number(
            db,
            truck_data.truck_number,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Truck number already exists.",
            )

        existing = await truck_repository.get_by_vin(
            db,
            truck_data.vin,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="VIN already exists.",
            )

        existing = await truck_repository.get_by_license_plate(
            db,
            truck_data.license_plate,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License plate already exists.",
            )

        truck = Truck(**truck_data.model_dump())

        return await truck_repository.create(
            db,
            truck,
        )

    async def get_truck(
        self,
        db: AsyncSession,
        truck_id: str,
    ) -> Truck:

        truck = await truck_repository.get_by_id(
            db,
            truck_id,
        )

        if not truck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Truck not found.",
            )

        return truck

    async def list_trucks(
        self,
        db: AsyncSession,
    ) -> list[Truck]:

        return await truck_repository.list_active(db)

    async def update_truck(
        self,
        db: AsyncSession,
        truck_id: str,
        truck_data: TruckUpdate,
    ) -> Truck:

        truck = await truck_repository.get_by_id(
            db,
            truck_id,
        )

        if not truck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Truck not found.",
            )

        updates = truck_data.model_dump(exclude_unset=True)

        if (
            "truck_number" in updates
            and updates["truck_number"] != truck.truck_number
        ):
            existing = await truck_repository.get_by_truck_number(
                db,
                updates["truck_number"],
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Truck number already exists.",
                )

        if (
            "vin" in updates
            and updates["vin"] != truck.vin
        ):
            existing = await truck_repository.get_by_vin(
                db,
                updates["vin"],
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="VIN already exists.",
                )

        if (
            "license_plate" in updates
            and updates["license_plate"] != truck.license_plate
        ):
            existing = await truck_repository.get_by_license_plate(
                db,
                updates["license_plate"],
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="License plate already exists.",
                )

        for field, value in updates.items():
            setattr(truck, field, value)

        return await truck_repository.update(
            db,
            truck,
        )

    async def delete_truck(
        self,
        db: AsyncSession,
        truck_id: str,
    ) -> Truck:

        truck = await truck_repository.get_by_id(
            db,
            truck_id,
        )

        if not truck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Truck not found.",
            )

        return await truck_repository.delete(
            db,
            truck,
        )


truck_service = TruckService()