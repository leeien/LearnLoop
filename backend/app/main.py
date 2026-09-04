from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.dashboard import router as dashboard_router
from app.api.goals import router as goals_router
from app.api.health import router as health_router
from app.api.harness import router as harness_router
from app.api.knowledge import router as knowledge_router
from app.api.leetcode import router as leetcode_router
from app.api.mastery import router as mastery_router
from app.api.memory import router as memory_router
from app.api.quiz import router as quiz_router
from app.api.rag import router as rag_router
from app.api.reminder import router as reminder_router
from app.api.reminders import router as reminders_router
from app.api.review import router as review_router
from app.api.tasks import router as tasks_router
from app.api.tools import router as tools_router
from app.core.config import get_settings
from app.core.database import init_db
from app.core.exceptions import ServiceError


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ServiceError)
async def service_error_handler(
    _: Request,
    exc: ServiceError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "data": None, "message": exc.message},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    error = exc.errors()[0] if exc.errors() else {}
    location = ".".join(str(part) for part in error.get("loc", []))
    detail = error.get("msg", "Invalid request.")
    message = f"{location}: {detail}" if location else detail
    return JSONResponse(
        status_code=422,
        content={"success": False, "data": None, "message": message},
    )


@app.exception_handler(HTTPException)
async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "data": None, "message": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled API error",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "message": "Internal server error.",
        },
    )


app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(harness_router, prefix=settings.api_prefix)
app.include_router(goals_router, prefix=settings.api_prefix)
app.include_router(tasks_router, prefix=settings.api_prefix)
app.include_router(tools_router, prefix=settings.api_prefix)
app.include_router(knowledge_router, prefix=settings.api_prefix)
app.include_router(leetcode_router, prefix=settings.api_prefix)
app.include_router(quiz_router, prefix=settings.api_prefix)
app.include_router(rag_router, prefix=settings.api_prefix)
app.include_router(memory_router, prefix=settings.api_prefix)
app.include_router(mastery_router, prefix=settings.api_prefix)
app.include_router(review_router, prefix=settings.api_prefix)
app.include_router(reminder_router, prefix=settings.api_prefix)
app.include_router(reminders_router, prefix=settings.api_prefix)
app.include_router(dashboard_router, prefix=settings.api_prefix)
