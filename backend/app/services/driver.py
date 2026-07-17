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
        driver = await self.repository.get_by_id(db, driver_id)

        if not driver:
            raise HTTPException(
                status_code=404,
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

    async def delete_driver(
        self,
        db: AsyncSession,
        driver_id: str,
    ):
        driver = await self.get_driver(db, driver_id)

        driver.is_active = False

        await db.commit()
        await db.refresh(driver)

        return driver


driver_service = DriverService()