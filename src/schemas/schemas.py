from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from models.models import TaskStatus


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


class DepartmentBase(BaseModel):
    name: str
    company_id: int
    parent_path: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    parent_path: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    company_id: int
    path: str

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    responsible_id: int
    observer_ids: List[int]
    executor_ids: List[int]
    deadline: Optional[str] = None
    estimated_time: Optional[float] = None


class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    responsible_id: int
    observer_ids: List[int]
    executor_ids: List[int]
    deadline: Optional[str]
    estimated_time: Optional[float]
    status: Optional[TaskStatus] = TaskStatus.NEW

    @field_validator("status", mode="before")
    def normalize_status(cls, value):
        if isinstance(value, str):
            value = value.title()
        return TaskStatus(value)


class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[TaskStatus]
    deadline: Optional[str]
    estimated_time: Optional[float]


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    responsible_id: int
    observer_ids: List[int]
    executor_ids: List[int]
    deadline: Optional[str] = None
    estimated_time: Optional[float] = None
    status: TaskStatus

    model_config = ConfigDict(from_attributes=True)
