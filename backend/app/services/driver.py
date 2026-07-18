from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver import Driver
from app.repositories.driver import driver_repository
from app.schemas.driver import DriverCreate, DriverUpdate


class DriverService:
    def __init__(self):
        self.repository = driver_repository

    async def create_driver(
        self,
        db: AsyncSession,
        payload: DriverCreate,
    ):
        existing_email = await self.repository.get_by_email(
            db,
            payload.email,
        )

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        existing_cdl = await self.repository.get_by_cdl(
            db,
            payload.cdl_number,
        )

        if existing_cdl:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CDL number already exists",
            )

        driver = Driver(**payload.model_dump())

        return await self.repository.create(db, driver)

    async def get_driver(
        self,
        db: AsyncSession,
        driver_id: str,
    ):
        driver = await self.repository.get_by_id(
            db,
            driver_id,
        )

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found",
            )

        return driver

    async def list_drivers(
        self,
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ):
        return await self.repository.list_active(
            db,
            limit,
            offset,
        )

    async def update_driver(
        self,
        db: AsyncSession,
        driver_id: str,
        payload: DriverUpdate,
    ):
        driver = await self.get_driver(
            db,
            driver_id,
        )

        updates = payload.model_dump(exclude_unset=True)

        if (
            "email" in updates
            and updates["email"] != driver.email
        ):
            existing = await self.repository.get_by_email(
                db,
                updates["email"],
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists",
                )

        if (
            "cdl_number" in updates
            and updates["cdl_number"] != driver.cdl_number
        ):
            existing = await self.repository.get_by_cdl(
                db,
                updates["cdl_number"],
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="CDL number already exists",
                )

        for field, value in updates.items():
            setattr(driver, field, value)

        return await self.repository.update(
            db,
            driver,
        )

    async def delete_driver(
        self,
        db: AsyncSession,
        driver_id: str,
    ):
        driver = await self.get_driver(
            db,
            driver_id,
        )

        return await self.repository.delete(
            db,
            driver,
        )


driver_service = DriverService()