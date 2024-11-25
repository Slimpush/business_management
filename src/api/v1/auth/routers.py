from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import EmailStr
from schemas.schemas import (
    ConfirmRegistrationRequest,
    ConfirmRegistrationResponse,
    SignUpRequestSchema,
    SignUpResponseSchema,
    CompleteSignUpRequest,
    CompleteSignUpResponse,
    CheckAccountResponse,
    SignInRequestSchema,
    TokenInfo,
    UserToken,
    UserUpdateRequest,
)
from utils.utils import get_current_user
from .services import AuthService

router = APIRouter()


@router.get("/api/v1/check_account/{account}", response_model=CheckAccountResponse)
async def check_account(
    account: EmailStr, service: AuthService = Depends()
) -> CheckAccountResponse:
    return await service.check_account(account=account)


@router.post("/api/v1/sign-up/", response_model=SignUpResponseSchema)
async def sign_up(
    schema: SignUpRequestSchema, service: AuthService = Depends()
) -> SignUpResponseSchema:
    return await service.sign_up(schema=schema)


@router.post("/api/v1/sign-up-complete/", response_model=CompleteSignUpResponse)
async def sign_up_complete(
    schema: CompleteSignUpRequest, service: AuthService = Depends()
) -> CompleteSignUpResponse:
    return await service.sign_up_complete(schema=schema)


@router.post("/api/v1/sign-in", response_model=TokenInfo)
async def sign_in(
    schema: SignInRequestSchema, service: AuthService = Depends()
) -> TokenInfo:
    return await service.sign_in(schema=schema)


@router.post("/api/v1/invite-employee/")
async def invite_employee(
    email: EmailStr,
    current_user: UserToken = Depends(get_current_user),
    service: AuthService = Depends(),
) -> dict:
    company_id = current_user.company_id
    return await service.invite_employee(email=email, company_id=company_id)


@router.patch("/api/v1/user/{user_id}")
async def update_user(
    user_id: int,
    schema: UserUpdateRequest,
    service: AuthService = Depends(),
    current_user: UserToken = Depends(get_current_user),
) -> dict:
    if user_id != current_user.user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied.")

    return await service.update_user(user_id=user_id, schema=schema)


@router.patch("/api/v1/user/{user_id}/update-email")
async def update_email(
    user_id: int,
    new_email: EmailStr,
    service: AuthService = Depends(),
    current_user: UserToken = Depends(get_current_user),
) -> dict:
    if user_id != current_user.user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied.")
    return await service.update_email(user_id=user_id, new_email=new_email)


@router.post("/api/v1/create-employee/")
async def create_employee(
    account: EmailStr,
    first_name: str,
    last_name: str,
    position_id: Optional[int] = None,
    current_user: UserToken = Depends(get_current_user),
    service: AuthService = Depends(),
) -> dict:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied.")

    return await service.create_employee(
        email=account,
        first_name=first_name,
        last_name=last_name,
        company_id=current_user.company_id,
        position_id=position_id,
    )


@router.post("/api/v1/confirm-invite/")
async def confirm_invite(
    schema: ConfirmRegistrationRequest, service: AuthService = Depends()
) -> ConfirmRegistrationResponse:
    return await service.confirm_invite(schema=schema)
