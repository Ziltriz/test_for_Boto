# exception_handlers.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.utils.exception import BaseAppException, UserAlreadyExistsError

def setup_exception_handlers(app: FastAPI):
    """Настройка обработчиков исключений"""
    
    @app.exception_handler(BaseAppException)
    async def base_app_exception_handler(request: Request, exc: BaseAppException):
        """Обработчик для всех кастомных исключений"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Обработчик для всех остальных исключений"""
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "Internal server error",
                "detail": str(exc) if app.debug else None
            }
        )