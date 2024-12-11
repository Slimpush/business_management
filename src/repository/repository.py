import logging
from typing import Any, List, Optional

from fastapi import HTTPException
from sqlalchemy import delete, select, text
from sqlalchemy.orm import selectinload
from sqlalchemy_utils.types.ltree import Ltree

from models.models import (
    Company,
    Department,
    Invite,
    Position,
    RoleAssignment,
    Task,
    User,
)
from utils.core_repository import SQLAlchemyBaseRepository


class UserRepository(SQLAlchemyBaseRepository):
    def __init__(self, session):
        super().__init__(session, User)

    async def get_all_subordinates(self, user_id: int) -> list:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.subordinates))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        def collect_subordinates(user):
            all_subordinates = []
            for subordinate in user.subordinates:
                all_subordinates.append(subordinate)
                all_subordinates.extend(collect_subordinates(subordinate))
            return all_subordinates

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
        self, name: str, company_id: int, parent_id: Optional[int] = None
    ) -> int:
        department = self.model(name=name, path=None, company_id=company_id)
        self.session.add(department)
        await self.session.flush()

        if parent_id:
            parent = await self.get_by_id(parent_id)
            if not parent:
                raise ValueError("Parent department not found")

            if not parent.path:
                raise ValueError("Parent path is not set")

            department.path = Ltree(f"{parent.path}.{department.id}")
        else:
            department.path = Ltree(f"{department.id}")

        self.session.add(department)
        await self.session.commit()

        return department.id

    async def get_descendants(self, department_id: int) -> list:
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")

        query = select(self.model).where(self.model.path.op("<@")(department.path))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_ancestors(self, department_id: int) -> list:
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")
        query = select(self.model).where(self.model.path.op("@>")(department.path))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_descendants_with_names(self, department_id: int) -> list[str]:
        descendants = await self.get_descendants(department_id)

        result = []
        for dep in descendants:
            visualized_path = await self.get_visualized_path(dep.id)
            result.append(visualized_path)

        return result

    async def get_ancestors_with_names(self, department_id: int) -> list[str]:
        ancestors = await self.get_ancestors(department_id)

        result = []
        for dep in ancestors:
            visualized_path = await self.get_visualized_path(dep.id)
            result.append(visualized_path)

        return result

    async def move_department_with_descendants(self, department_id: int, new_parent_path: str):
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")

        old_path = str(department.path)
        new_path = f"{new_parent_path}.{department.id}"

        department.path = Ltree(new_path)
        self.session.add(department)

        descendants = await self.session.execute(
            text("""
            SELECT id, path::text
            FROM departments
            WHERE path <@ :old_path AND path != :old_path
            """),
            {"old_path": old_path},
        )

        descendants = descendants.fetchall()

        for descendant in descendants:
            descendant_id = descendant.id
            descendant_old_path = descendant.path

            relative_path = descendant_old_path[len(old_path) + 1:]

            descendant_new_path = f"{new_path}.{relative_path}"

            await self.session.execute(
                text("""
                UPDATE departments
                SET path = :new_path
                WHERE id = :id
                """),
                {"new_path": descendant_new_path, "id": descendant_id},
            )

        await self.session.commit()

    async def get_by_id(self, obj_id: int) -> Optional[Any]:
        obj = await self.session.get(self.model, obj_id)
        if obj is None:
            logging.warning(f"Object with ID {obj_id} not found")
        elif not isinstance(obj, Department):
            logging.error(f"Unexpected object type: {type(obj)}")
        return obj

    async def delete_by_query(self, department_id: int):
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")

        query = delete(self.model).where(self.model.path.op("<@")(department.path))
        await self.session.execute(query)
        await self.session.commit()

    async def move_department(self, department_id: int, new_parent_path: str):
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")
        department.path = f"{new_parent_path}.{department.name}"
        self.session.add(department)
        await self.session.commit()

    async def get_visualized_path(self, department_id: int) -> str:
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")
        path_str = str(department.path)
        path_ids = path_str.split(".")

        path_names = []
        for id in path_ids:
            dep = await self.get_by_id(int(id))
            if not dep:
                raise ValueError(f"Department with ID {id} not found in path {path_str}")
            if dep:
                path_names.append(dep.name)

        return ".".join(path_names)


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


class TaskRepository(SQLAlchemyBaseRepository):
    def __init__(self, session):
        super().__init__(session, Task)
