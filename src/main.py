from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from api.v1.auth.routers import router
from utils.jwt import auth_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(router, prefix="/auth", tags=["auth"])
app.middleware("http")(auth_middleware)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
