from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
from pydantic import computed_field


load_dotenv()


class AuthJWT:
    private_key_path: Path = Path(
        Path(__file__).parent / "utils" / "certs" / "private.pem"
    )
    public_key_path: Path = Path(
        Path(__file__).parent / "utils" / "certs" / "public.pem"
    )
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15


class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    auth_jwt: AuthJWT = AuthJWT()

    class Config:
        env_file = ".env"


settings = Settings()
