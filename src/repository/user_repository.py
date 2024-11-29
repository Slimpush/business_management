import logging
from typing import Any, List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy_utils.types.ltree import Ltree

from models.models import (Company, Department, Invite, Position,
                           RoleAssignment, User)
from utils.repository import SQLAlchemyBaseRepository


class UserRepository(SQLAlchemyBaseRepository):
    def __init__(self, session):
        super().__init__(session, User)

    async def get_all_subordinates(self, user_id: int) -> list:
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        def collect_subordinates(user):
            subordinates = user.subordinates
            for subordinate in user.subordinates:
                subordinates.extend(collect_subordinates(subordinate))
            return subordinates

        all_subordinates = collect_subordinates(user)
        return [sub.dict() for sub in all_subordinates]


class CompanyRepository(SQLAlchemyBaseRepository):
    def __init__(self, session):
        super().__init__(session, Company)


class PositionRepository(SQLAlchemyBaseRepository):
    def __init__(self, session):
        super().__init__(session, Position)


class InviteRepository(SQLAlchemyBaseRepository):
    def __init__(self, session):
        super().__init__(session, Invite)


class DepartmentRepository(SQLAlchemyBaseRepository):
    def __init__(self, session, model=Department):
        super().__init__(session, Department)

    async def add_one_and_get_id(self, **kwargs) -> int:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        return obj.id

    async def add_one(
        self, name: str, company_id: int, parent_path: Optional[str] = None
    ):
        new_path = f"{parent_path}.{name}" if parent_path else name
        ltree_path = Ltree(new_path)
        query = self.model(name=name, path=ltree_path, company_id=company_id)
        self.session.add(query)
        await self.session.commit()
        return query.id

    async def get_descendants(self, department_id: int) -> list:
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")

        query = select(self.model).where(self.model.path.descendant_of(department.path))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_ancestors(self, department_id: int) -> list:
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")

        query = select(self.model).where(self.model.path.ancestor_of(department.path))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def move_department_with_descendants(
        self, department_id: int, new_parent_path: str
    ):
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")

        old_path = department.path
        new_path = f"{new_parent_path}.{department.name}"
        department.path = Ltree(new_path)
        self.session.add(department)

        descendants = await self.get_descendants(department_id)
        for descendant in descendants:
            relative_path = descendant.path[len(old_path) + 1 :]
            descendant.path = Ltree(f"{new_path}.{relative_path}")
            self.session.add(descendant)

        await self.session.commit()

    async def get_by_id(self, obj_id: int) -> Optional[Any]:
        obj = await self.session.get(self.model, obj_id)
        if obj is None:
            logging.warning(f"Object with ID {obj_id} not found")
        elif not isinstance(obj, Department):
            logging.error(f"Unexpected object type: {type(obj)}")
        return obj

    async def move_department(self, department_id: int, new_parent_path: str):
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")
        department.path = f"{new_parent_path}.{department.name}"
        self.session.add(department)
        await self.session.commit()


class RoleAssignmentRepository(SQLAlchemyBaseRepository):
    def __init__(self, session):
        super().__init__(session, RoleAssignment)

    async def get_by_query_all(self, user_id: int) -> List[RoleAssignment]:
        result = await self.session.execute(
            select(RoleAssignment).where(RoleAssignment.user_id == user_id)
        )
        return result.scalars().all()

    async def add_one(self, user_id: int, department_id: int, role_name: str):
        new_assignment = RoleAssignment(
            user_id=user_id,
            department_id=department_id,
            role_name=role_name,
        )
        self.session.add(new_assignment)
        await self.session.commit()
