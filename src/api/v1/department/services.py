from typing import Optional

from fastapi import HTTPException

from schemas.schemas import UserToken
from utils.service import BaseService
from utils.unit_of_work import transaction_mode


class OrganizationService(BaseService):
    @transaction_mode
    async def create_department(
        self,
        name: str,
        company_id: int,
        current_user: UserToken,
        parent_id: Optional[int] = None,
    ):
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        parent_path = None
        if parent_id:
            parent = await self.uow.department.get_by_id(parent_id)
            if not parent:
                raise HTTPException(
                    status_code=404, detail="Parent department not found"
                )
            parent_path = parent.path

        await self.uow.department.add_one(
            name=name, company_id=company_id, parent_path=parent_path
        )

    @transaction_mode
    async def get_descendants(
        self,
        department_id: int,
        current_user: UserToken,
    ) -> list:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        return await self.uow.department.get_descendants(department_id)

    @transaction_mode
    async def get_ancestors(
        self,
        department_id: int,
        current_user: UserToken,
    ) -> list:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        return await self.uow.department.get_ancestors(department_id)

    @transaction_mode
    async def move_department(
        self,
        department_id: int,
        new_parent_id: int,
        current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        new_parent = await self.uow.department.get_by_id(new_parent_id)
        if not new_parent:
            raise HTTPException(
                status_code=404, detail="New parent department not found"
            )

        await self.uow.department.move_department_with_descendants(
            department_id, new_parent.path
        )
        return {"message": "Department moved successfully"}

    @transaction_mode
    async def update_department(
        self,
        department_id: int,
        name: Optional[str],
        parent_id: Optional[int],
        current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        updates = {"name": name, "parent_id": parent_id}
        updates = {k: v for k, v in updates.items() if v is not None}

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update.")

        await self.uow.department.update_one_by_id(obj_id=department_id, **updates)
        return {"message": "Department updated successfully."}

    @transaction_mode
    async def delete_department(
        self,
        department_id: int,
        current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")

        department = await self.uow.department.get_by_id(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        await self.uow.department.delete_by_query(id=department_id)
        return {"message": "Department deleted successfully"}

    @transaction_mode
    async def create_position(
        self,
        name: str,
        description: Optional[str],
        company_id: int,
        current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        position_id = await self.uow.position.add_one_and_get_id(
            name=name, description=description, company_id=company_id
        )
        return {"message": "Position created successfully.", "position_id": position_id}

    @transaction_mode
    async def update_position(
        self,
        position_id: int,
        name: Optional[str],
        description: Optional[str],
        current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        updates = {"name": name, "description": description}
        updates = {k: v for k, v in updates.items() if v is not None}

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update.")

        await self.uow.position.update_one_by_id(obj_id=position_id, **updates)
        return {"message": "Position updated successfully."}

    @transaction_mode
    async def delete_position(
        self,
        position_id: int,
        current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        await self.uow.position.delete_one_by_id(obj_id=position_id)
        return {"message": "Position deleted successfully."}

    @transaction_mode
    async def assign_position_to_department(
        self,
        position_id: int,
        department_id: int,
        current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        position = await self.uow.position.get_by_query_one_or_none(id=position_id)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found.")

        await self.uow.position.update_one_by_id(
            obj_id=position_id, department_id=department_id
        )

        updated_position = await self.uow.position.get_by_query_one_or_none(
            id=position_id
        )

        return {
            "message": "Position assigned to department successfully.",
            "position_id": updated_position.id,
            "department_id": updated_position.department_id,
        }

    @transaction_mode
    async def assign_position_to_user(
        self,
        position_id: int,
        user_id: int,
        current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        position = await self.uow.position.get_by_id(position_id)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found.")

        user = await self.uow.user.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        if position.company_id != user.company_id:
            raise HTTPException(
                status_code=400,
                detail="Position and user must belong to the same company.",
            )

        await self.uow.position.update_one_by_id(obj_id=position_id, user_id=user_id)

        return {"message": "Position assigned to user successfully"}

    @transaction_mode
    async def assign_manager(
        self,
        department_id: int,
        user_id: int,
        current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        department = await self.uow.department.get_by_id(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        await self.uow.department.update_one_by_id(department_id, manager_id=user_id)
        return {"message": "Manager assigned successfully"}

    @transaction_mode
    async def get_subordinates(
        self,
        user_id: int,
        current_user: UserToken,
    ) -> list:
        if not current_user.is_admin and current_user.user_id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        subordinates = await self.uow.user.get_all_subordinates(user_id)
        return [sub.dict() for sub in subordinates]

    @transaction_mode
    async def assign_role(
        self,
        user_id: int,
        department_id: int,
        role_name: str,
        current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        user = await self.uow.user.get_by_id(user_id)
        department = await self.uow.department.get_by_id(department_id)

        if not user or not department:
            raise HTTPException(status_code=404, detail="User or Department not found.")

        await self.uow.role_assignment.add_one(
            user_id=user_id, department_id=department_id, role_name=role_name
        )
        return {"message": "Role assigned successfully."}

    @transaction_mode
    async def get_roles(
        self,
        user_id: int,
        current_user: UserToken,
    ) -> list:
        if not current_user.is_admin and current_user.user_id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        roles = await self.uow.role_assignment.get_by_query_all(user_id=user_id)
        return [
            {"department_id": role.department_id, "role_name": role.role_name}
            for role in roles
        ]
