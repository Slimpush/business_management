from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from pydantic import EmailStr

from schemas.schemas import (
    CheckAccountResponse,
    CompleteSignUpRequest,
    CompleteSignUpResponse,
    ConfirmRegistrationRequest,
    ConfirmRegistrationResponse,
    SignInRequestSchema,
    SignUpRequestSchema,
    SignUpResponseSchema,
    TokenInfo,
    UserToken,
    UserUpdateRequest,
)
from utils.service import BaseService
from utils.unit_of_work import transaction_mode
from utils.utils import (
    encode_jwt,
    generate_invite_token,
    hash_password,
    validate_password,
)


class AuthService(BaseService):
    @transaction_mode
    async def check_account(self, account: EmailStr) -> CheckAccountResponse:
        user_exists = await self.uow.user.get_by_query_one_or_none(email=account)
        if user_exists:
            raise HTTPException(status_code=400, detail="Email already in use.")

        default_company = await self.uow.company.get_by_query_one_or_none(
            name="Default Company"
        )
        if not default_company:
            default_company_id = await self.uow.company.add_one_and_get_id(
                name="Default Company"
            )
        else:
            default_company_id = default_company.id

        invite = await self.uow.invite.get_by_query_one_or_none(email=account)
        invite_token = invite.token if invite else generate_invite_token()

        if invite and not invite.is_verified:
            await self.uow.invite.update_one_by_id(
                obj_id=invite.id,
                token=invite_token,
            )
        elif not invite:
            await self.uow.invite.add_one(
                email=account,
                token=invite_token,
                company_id=default_company_id,
            )

        return CheckAccountResponse(
            message="Verification code generated.",
            account=account,
            invite_token=invite_token,
        )

    @transaction_mode
    async def sign_up(self, schema: SignUpRequestSchema) -> SignUpResponseSchema:
        invite = await self.uow.invite.get_by_query_one_or_none(email=schema.account)
        if not invite or invite.token != schema.token:
            raise HTTPException(
                status_code=400,
                detail="Invalid or missing verification code.",
            )

        await self.uow.invite.update_one_by_id(obj_id=invite.id, is_verified=True)
        return SignUpResponseSchema(
            message="Account successfully verified.",
            account=schema.account,
        )

    @transaction_mode
    async def sign_up_complete(
        self, schema: CompleteSignUpRequest
    ) -> CompleteSignUpResponse:
        invite = await self.uow.invite.get_by_query_one_or_none(email=schema.account)
        if not invite or not invite.is_verified:
            raise HTTPException(
                status_code=400,
                detail="Account not verified.",
            )

        company_exists = await self.uow.company.get_by_query_one_or_none(
            name=schema.company_name
        )
        if company_exists:
            raise HTTPException(
                status_code=400,
                detail="Company name already in use.",
            )

        hashed_password = hash_password(schema.password)
        company_id = await self.uow.company.add_one_and_get_id(name=schema.company_name)
        user_data = {
            "email": schema.account,
            "first_name": schema.first_name,
            "last_name": schema.last_name,
            "hashed_password": hashed_password,
            "is_admin": True,
            "company_id": company_id,
            "position_id": None,
        }
        await self.uow.user.add_one(**user_data)

        return CompleteSignUpResponse(
            account=schema.account,
            password=hashed_password,
            first_name=schema.first_name,
            last_name=schema.last_name,
            company_name=schema.company_name,
        )

    @transaction_mode
    async def sign_in(self, schema: SignInRequestSchema) -> TokenInfo:
        user = await self._validate_auth_user(
            schema.account,
            schema.password,
        )

        current_time = datetime.now(timezone.utc)
        jwt_payload = {
            "sub": user.id,
            "company_id": user.company_id,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "iat": int(current_time.timestamp()),
        }
        token = encode_jwt(jwt_payload)

        return TokenInfo(access_token=token, token_type="Bearer")

    async def _validate_auth_user(self, email: str, password: str):
        user = await self.uow.user.get_by_query_one_or_none(email=email)

        if not user:
            raise HTTPException(
                status_code=400,
                detail="User with this email does not exist.",
            )
        if not validate_password(
            password=password,
            hashed_password=user.hashed_password,
        ):
            raise HTTPException(
                status_code=400,
                detail="Incorrect password.",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="User account is inactive.",
            )

        return user

    @transaction_mode
    async def invite_employee(self, email: EmailStr, company_id: int) -> dict:
        invite = await self.uow.invite.get_by_query_one_or_none(email=email)

        if invite:
            if invite.is_verified:
                raise HTTPException(status_code=400, detail="User already verified.")
            invite_token = generate_invite_token()
            await self.uow.invite.update_one_by_id(obj_id=invite.id, token=invite_token)
        else:
            invite_token = generate_invite_token()
            await self.uow.invite.add_one(
                email=email, token=invite_token, company_id=company_id
            )

        return {
            "message": "Invite successfully generated.",
            "email": email,
            "invite_token": invite_token,
        }

    @transaction_mode
    async def update_user(
        self,
        user_id: int,
        schema: UserUpdateRequest,
        current_user: UserToken,
    ) -> dict:
        user = await self.uow.user.get_by_query_one_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        if user_id != current_user.user_id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied.")
        updates = schema.model_dump(exclude_unset=True)
        updates.pop("position_id", None)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update.")

        await self.uow.user.update_one_by_id(obj_id=user_id, **updates)
        return {
            "message": "User updated successfully.",
            "updated_fields": list(updates.keys()),
        }

    @transaction_mode
    async def update_email(
        self,
        user_id: int,
        new_email: EmailStr,
        current_user: UserToken,
    ) -> dict:
        existing_user = await self.uow.user.get_by_query_one_or_none(email=new_email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use.")
        if user_id != current_user.user_id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied.")

        await self.uow.user.update_one_by_id(obj_id=user_id, email=new_email)
        return {"message": "Email updated successfully."}

    @transaction_mode
    async def create_employee(
        self,
        email: EmailStr,
        first_name: str,
        last_name: str,
        company_id: int,
        current_user: UserToken,
        position_id: Optional[int] = None,
    ) -> dict:
        user_exists = await self.uow.user.get_by_query_one_or_none(email=email)
        if user_exists:
            raise HTTPException(status_code=400, detail="User already exists.")

        invite_exists = await self.uow.invite.get_by_query_one_or_none(email=email)
        if invite_exists and invite_exists.is_verified:
            raise HTTPException(status_code=400, detail="Invite already verified.")

        invite_token = generate_invite_token()

        temp_password = hash_password("temporary_password")

        await self.uow.user.add_one(
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=temp_password,
            is_admin=False,
            is_active=False,
            company_id=company_id,
            position_id=position_id,
        )

        await self.uow.invite.add_one(
            email=email, token=invite_token, company_id=company_id
        )

        return {
            "message": "Employee created and invite generated.",
            "invite_token": invite_token,
        }

    @transaction_mode
    async def confirm_invite(
        self, schema: ConfirmRegistrationRequest
    ) -> ConfirmRegistrationResponse:
        invite = await self.uow.invite.get_by_query_one_or_none(email=schema.account)
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found.")
        if invite.token != schema.token:
            raise HTTPException(status_code=400, detail="Invalid invite token.")
        if invite.is_verified:
            raise HTTPException(status_code=400, detail="Invite already used.")

        user = await self.uow.user.get_by_query_one_or_none(email=schema.account)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        hashed_password = hash_password(schema.password)
        await self.uow.user.update_one_by_id(
            obj_id=user.id,
            hashed_password=hashed_password,
            is_active=True,
        )
        await self.uow.invite.update_one_by_id(obj_id=invite.id, is_verified=True)

        return ConfirmRegistrationResponse(
            message="Registration completed successfully."
        )
