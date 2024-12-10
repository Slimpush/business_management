from fastapi import FastAPI, HTTPException, Depends
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import pytest

from src.schemas.schemas import SignInRequestSchema, SignUpData, SignUpResponseSchema, TokenInfo


@pytest.fixture(scope="function")
def api_client_without_auth():
    client = TestClient(app)
    return client


class AuthService:
    fake_db = {}

    async def sign_up(self, schema: SignUpData) -> SignUpResponseSchema:
        if schema.token != "valid-invite-token":
            raise HTTPException(status_code=400, detail="Invalid or missing verification code.")
        self.fake_db[schema.account] = schema.password
        return SignUpResponseSchema(message="Account successfully verified.", account=schema.account)

    async def sign_in(self, schema: SignInRequestSchema) -> TokenInfo:
        password = self.fake_db.get(schema.account)
        if not password or password != schema.password:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        current_time = datetime.now(timezone.utc)
        jwt_payload = {
            "sub": schema.account,
            "iat": int(current_time.timestamp()),
        }
        token = "fake-jwt-token"
        return TokenInfo(access_token=token, token_type="Bearer")


app = FastAPI()
auth_service = AuthService()


@app.post("/api/v1/sign-up/", response_model=SignUpResponseSchema)
async def sign_up(schema: SignUpData, service: AuthService = Depends()) -> SignUpResponseSchema:
    return await service.sign_up(schema=schema)


@app.post("/api/v1/sign-in", response_model=TokenInfo)
async def sign_in(schema: SignInRequestSchema, service: AuthService = Depends()) -> TokenInfo:
    return await service.sign_in(schema=schema)

