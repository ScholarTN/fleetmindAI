from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver import Driver
from app.repositories.base import BaseRepository


class DriverRepository(BaseRepository[Driver]):
    def __init__(self):
        super().__init__(Driver)

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str,
    ):
        result = await db.execute(
            select(Driver).where(Driver.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_cdl(
        self,
        db: AsyncSession,
        cdl_number: str,
    ):
        result = await db.execute(
            select(Driver).where(
                Driver.cdl_number == cdl_number
            )
        )
        return result.scalar_one_or_none()

    async def list_active(
        self,
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ):
        result = await db.execute(
            select(Driver)
            .where(Driver.is_active == True)
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()


driver_repository = DriverRepository()