from typing import Optional
from pydantic import BaseModel, EmailStr


class CheckAccountResponse(BaseModel):
    message: str
    account: EmailStr
    invite_token: Optional[str] = None


class SignUpRequestSchema(BaseModel):
    account: EmailStr
    token: str


class SignUpResponseSchema(BaseModel):
    account: EmailStr
    message: str


class SignInRequestSchema(BaseModel):
    account: EmailStr
    password: str


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


class UserToken(BaseModel):
    user_id: int
    company_id: int
    is_admin: bool


class CompleteSignUpRequest(BaseModel):
    account: EmailStr
    invite_token: str
    first_name: str
    last_name: str
    company_name: str
    password: str


class CompleteSignUpResponse(BaseModel):
    account: EmailStr
    first_name: str
    last_name: str
    company_name: str
    password: str


class UserUpdateRequest(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    position_id: Optional[int] = None


class ConfirmRegistrationRequest(BaseModel):
    account: EmailStr
    token: str
    password: str


class ConfirmRegistrationResponse(BaseModel):
    message: str
