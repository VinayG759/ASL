from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from asl.api.exception_handlers import validation_exception_handler
from asl.api.middleware.errors import ErrorHandlerMiddleware
from asl.api.router import api_router
from asl.config import settings
from asl.persistence.database import async_session_factory, engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Agentic Safety Layer",
        version="0.1.0",
        docs_url="/api/v1/docs",
        openapi_url="/api/v1/openapi.json",
        lifespan=lifespan,
    )
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.include_router(api_router, prefix="/api/v1")
    app.state.settings = settings
    app.state.async_session_factory = async_session_factory
    return app


app = create_app()
