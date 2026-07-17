from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    def __init__(self, repository):
        self.repository = repository

    async def get(self, db: AsyncSession, obj_id: str):
        return await self.repository.get_by_id(db, obj_id)

    async def list(self, db: AsyncSession, limit: int = 100, offset: int = 0):
        return await self.repository.get_all(db, limit, offset)