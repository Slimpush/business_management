import uuid
from datetime import datetime, timedelta, timezone
from typing import Union

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from schemas.schemas import UserToken
from settings import settings

http_bearer = HTTPBearer()


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: Union[timedelta, None] = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: Union[str, bytes],
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    payload = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
        options={"verify_sub": False},
    )

    if "sub" not in payload:
        raise ValueError("Invalid token: 'sub' claim is missing.")
    if not isinstance(payload["sub"], str):
        payload["sub"] = str(payload["sub"])

    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode("utf-8")


def validate_password(password: str, hashed_password: str) -> bool:
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password_bytes)


def generate_invite_token() -> str:
    return str(uuid.uuid4())


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> UserToken:
    token = credentials.credentials
    payload: dict = decode_jwt(token=token)
    user_id: int = payload.get("sub")
    company_id: int = payload.get("company_id")
    is_admin: bool = payload.get("is_admin")
    is_active: bool = payload.get("is_active")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    return UserToken(user_id=user_id, company_id=company_id, is_admin=is_admin)




