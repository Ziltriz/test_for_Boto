from typing import Optional

class BaseAppException(Exception):
    """Базовое исключение приложения"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserAlreadyExistsError(BaseAppException):
    """Исключение при попытке создать существующего пользователя"""
    def __init__(
        self, 
        message: Optional[str] = None,
        login: Optional[str] = None,
        email: Optional[str] = None
    ):
        if not message:
            if login and email:
                message = f"Пользователь с логином '{login}' или email '{email}' уже существует"
            elif login:
                message = f"Пользователь с логином '{login}' уже существует"
            elif email:
                message = f"Пользователь с email '{email}' уже существует"
            else:
                message = "Пользователь уже существует"
        
        super().__init__(message, status_code=409)