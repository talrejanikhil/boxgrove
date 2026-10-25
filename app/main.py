from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import STATIC_DIR, router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="Boxgrove", lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
