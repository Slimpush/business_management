import re

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from repository.user_repository import UserRepository

from .unit_of_work import UnitOfWork
from .utils import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/sign-in")


async def auth_middleware(request: Request, call_next):
    uow = UnitOfWork()
    user_repo = UserRepository(uow.session)

    public_paths = [
        r"^/auth/api/v1/check_account/[^/]+$",
        r"^/auth/api/v1/sign-in$",
        r"^/auth/api/v1/sign-up$",
        r"^/auth/api/v1/sign-up-verify$",
        r"^/auth/api/v1/sign-up-complete$",
        r"^/auth/api/v1/invite-employee/$",
        r"^/auth/api/v1/user/\d+/update-email$",
        r"^/auth/api/v1/confirm-invite",
        r"^/docs$",
        r"^/redoc$",
        r"^/openapi.json$",
    ]

    normalized_path = request.url.path.rstrip("/")
    if any(re.match(path, normalized_path) for path in public_paths):
        return await call_next(request)

    try:
        token = await oauth2_scheme(request)
        payload = decode_jwt(token)

        user_id = int(payload["sub"])
        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=403, detail="Inactive account")

        request.state.user = {
            "id": user.id,
            "company_id": user.company_id,
            "is_admin": user.is_admin,
        }
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    return await call_next(request)
