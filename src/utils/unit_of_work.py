import functools
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, NoReturn, Optional

from sqlalchemy.orm import sessionmaker

from database.db import async_session_maker
from repository.user_repository import (CompanyRepository, InviteRepository,
                                        PositionRepository,
                                        RoleAssignmentRepository,
                                        UserRepository)
from utils.repository import DepartmentRepository

from .custom_type import AsyncFunc


class AbstractUnitOfWork(ABC):

    user: UserRepository

    @abstractmethod
    def __init__(self) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> NoReturn:
        raise NotImplementedError


class UnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory: sessionmaker = None) -> None:
        self.session_factory = session_factory or async_session_maker
        self.session = self.session_factory()

    async def __aenter__(self) -> None:
        self.session = self.session_factory()
        self.user = UserRepository(self.session)
        self.company = CompanyRepository(self.session)
        self.position = PositionRepository(self.session)
        self.invite = InviteRepository(self.session)
        self.department = DepartmentRepository(self.session)
        self.role_assignment = RoleAssignmentRepository(self.session)

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()


def transaction_mode(func: AsyncFunc) -> AsyncFunc:

    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        async with self.uow:
            return await func(self, *args, **kwargs)

    return wrapper


def get_uow() -> UnitOfWork:
    return UnitOfWork()
