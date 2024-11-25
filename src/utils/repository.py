from abc import ABC, abstractmethod
from typing import Any, Optional, Sequence

from sqlalchemy import insert, select, delete
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Position


class AbstractRepository(ABC):

    @abstractmethod
    async def add_one(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def add_one_and_get_id(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    async def add_one_and_get_obj(self, *args, **kwargs) -> Optional[Any]:
        raise NotImplementedError

    async def get_by_query_one_or_none(self, *args, **kwargs) -> Optional[Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_query_all(self, *args, **kwargs) -> Sequence[Any]:
        raise NotImplementedError

    @abstractmethod
    async def update_one_by_id(self, obj_id: int, **kwargs) -> Optional[Any]:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_query(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_all(self) -> None:
        raise NotImplementedError


class SQLAlchemyBaseRepository(AbstractRepository):

    def __init__(self, session: AsyncSession, model: Any) -> None:
        self.session = session
        self.model = model

    async def add_one(self, **kwargs) -> None:
        kwargs.setdefault("company_id", 1)

        if kwargs.get("position_id") is not None:
            position = await self.session.execute(
                select(Position).where(Position.id == kwargs["position_id"])
            )
            if position.scalar() is None:
                raise ValueError(f"Invalid position_id: {kwargs['position_id']}")

        query = insert(self.model).values(**kwargs)
        try:
            await self.session.execute(query)
            await self.session.commit()
        except Exception as exc:
            await self.session.rollback()
            raise ValueError(f"Failed to execute query: {query}") from exc

    async def add_one_and_get_id(self, **kwargs) -> Any:
        query = insert(self.model).values(**kwargs).returning(self.model.id)
        result: Result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one()

    async def add_one_and_get_obj(self, **kwargs) -> Optional[Any]:
        obj_id = await self.add_one_and_get_id(**kwargs)
        return await self.get_by_query_one_or_none(id=obj_id)

    async def get_by_query_one_or_none(self, **kwargs) -> Optional[Any]:
        query = select(self.model).filter_by(**kwargs)
        result: Result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_query_all(self, **kwargs) -> Sequence[Any]:
        query = select(self.model).filter_by(**kwargs)
        result: Result = await self.session.execute(query)
        return result.scalars().all()

    async def update_one_by_id(self, obj_id: int, **kwargs) -> Optional[Any]:
        obj = await self.session.get(self.model, obj_id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            await self.session.commit()
            await self.session.refresh(obj)
        return obj

    async def delete_by_query(self, **kwargs) -> None:
        query = delete(self.model).filter_by(**kwargs)
        await self.session.execute(query)
        await self.session.commit()

    async def delete_all(self) -> None:
        query = delete(self.model)
        await self.session.execute(query)
        await self.session.commit()

    async def get_by_id(self, obj_id: int) -> Optional[Any]:
        return await self.session.get(self.model, obj_id)
