from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from schemas.schemas import UserToken
from utils.utils import get_current_user

from .services import OrganizationService

router = APIRouter()


@router.post("/api/v1/department/")
async def create_department(
    name: str,
    parent_id: Optional[int] = None,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.create_department(
        name=name,
        company_id=current_user.company_id,
        parent_id=parent_id,
    )


@router.get("/api/v1/department/{department_id}/descendants")
async def get_descendants(
    department_id: int,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.get_descendants(department_id)


@router.get("/api/v1/department/{department_id}/ancestors")
async def get_ancestors(
    department_id: int,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.get_ancestors(department_id)


@router.patch("/api/v1/department/{department_id}/move")
async def move_department(
    department_id: int,
    new_parent_id: int,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.move_department(department_id, new_parent_id)


@router.patch("/api/v1/department/{department_id}")
async def update_department(
    department_id: int,
    name: Optional[str] = None,
    parent_id: Optional[int] = None,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.update_department(
        department_id=department_id,
        name=name,
        parent_id=parent_id,
    )


@router.delete("/departments/{department_id}")
async def delete_department(
    department_id: int,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.delete_department(department_id=department_id)


@router.post("/api/v1/department/{department_id}/assign-manager/")
async def assign_manager(
    department_id: int,
    user_id: int,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.assign_manager(department_id=department_id, user_id=user_id)


@router.post("/api/v1/positions/")
async def create_position(
    name: str,
    description: Optional[str] = None,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.create_position(
        name=name,
        description=description,
        company_id=current_user.company_id,
    )


@router.patch("/api/v1/positions/{position_id}")
async def update_position(
    position_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.update_position(
        position_id=position_id,
        name=name,
        description=description,
    )


@router.delete("/api/v1/positions/{position_id}")
async def delete_position(
    position_id: int,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.delete_position(position_id=position_id)


@router.post("/api/v1/positions/{position_id}/assign-department/")
async def assign_position_to_department(
    position_id: int,
    department_id: int,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.assign_position_to_department(
        position_id=position_id,
        department_id=department_id,
    )


@router.post("/api/v1/positions/{position_id}/assign-user/")
async def assign_position_to_user(
    position_id: int,
    user_id: int,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.assign_position_to_user(
        position_id=position_id,
        user_id=user_id,
    )


@router.get("/api/v1/employees/{user_id}/subordinates/")
async def get_subordinates(
    user_id: int,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.get_subordinates(user_id=user_id)


@router.post("/api/v1/users/{user_id}/assign-role/")
async def assign_role(
    user_id: int,
    department_id: int,
    role_name: str,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.assign_role(user_id, department_id, role_name)


@router.get("/api/v1/users/{user_id}/roles/")
async def get_roles(
    user_id: int,
    current_user: UserToken = Depends(get_current_user),
    service: OrganizationService = Depends(),
):
    if not current_user.is_admin and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await service.get_roles(user_id)
