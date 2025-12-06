from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs: Any) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: UUID) -> ModelType | None:
        result = await self.session.execute(select(self.model).where(self.model.id == id))  # type: ignore[attr-defined]
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await self.session.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update(self, id: UUID, **kwargs: Any) -> ModelType | None:
        stmt = update(self.model).where(self.model.id == id).values(**kwargs).returning(self.model)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, id: UUID) -> bool:
        stmt = delete(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0  # type: ignore[no-any-return,attr-defined]
