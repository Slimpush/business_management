from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.v1.auth.routers import router
from api.v1.department.routers import router as d_router
from api.v1.tasks.routers import router as t_router
from utils.jwt import auth_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(router, prefix="/auth", tags=["auth"])
app.include_router(d_router, prefix="/dep", tags=["dep"])
app.include_router(t_router, prefix="/tasks", tags=["tasks"])
app.middleware("http")(auth_middleware)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
