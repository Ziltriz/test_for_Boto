from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from src.api import routers
from src.core.config import settings
from src.db.session import on_startup
from src.core.log_manager import LogManager

from src.api.exception_handlers import setup_exception_handlers

tags_metadata = [
    {
        "name": "health",
        "description": "Health check for api",
    },
]

app = FastAPI(
    title="fastapi-backend-base",
    description="base project for fastapi backend",
    version=settings.VERSION,
    openapi_url=f"/{settings.VERSION}/openapi.json",
    openapi_tags=tags_metadata,
)

LogManager.setup_loggers()

app.add_middleware(CORSMiddleware, allow_origins=["*"])

setup_exception_handlers(app)

app.add_event_handler("startup", on_startup)


app.include_router(routers.api_router)