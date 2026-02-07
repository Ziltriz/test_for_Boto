import logging

from fastapi import APIRouter, Depends, HTTPException, status, Body

from src.services.security import validate_api_key, get_password_hash
from src.utils.exception import UserAlreadyExistsError
from src.services.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    verify_password,
)
from src.schemas.request import (
    UserCredentials,
    TokenResponse,
    UserWithRelationsResponse,
    UserRegister,
    emailAdd,
    emailUpdate,
    tokenAdd
)
from src.schemas.response import SuccessResponse

from src.models.users import User
from backend.src.db.clients.lite_client import PostgresUserDbClient


router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=TokenResponse,
    summary="Аутентификация пользователя",
    description="Получение JWT токена доступа по логину/email и паролю",
    responses={
        200: {
            "description": "Успешная аутентификация",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "access_token": "eyJhbGciOi...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        400: {
            "description": "Неверный метод аутентификации",
            "content": {
                "application/json": {"example": {"detail": "Invalid authentication method"}}
            },
        },
        401: {
            "description": "Неверные учетные данные",
            "content": {"application/json": {"example": {"detail": "Incorrect login or password"}}},
        },
    },
)
async def login_for_access_token(
    credentials: UserCredentials,  # api_key: str = Depends(validate_api_key)
) -> TokenResponse:
    """
    Аутентификация пользователя и выдача JWT токена.

    Поддерживает несколько методов аутентификации:
    - по логину (method_auth="login")
    - по email (method_auth="email")

    Args:
        credentials: Объект с учетными данными пользователя:
            - login: Логин или email в зависимости от method_auth
            - password: Пароль
            - method_auth: Метод аутентификации ("login" или "email")
        api_key: Ключ API для защиты endpoint

    Returns:
        TokenResponse: Объект с JWT токеном доступа

    Raises:
        HTTPException:
            400 - если указан неверный метод аутентификации
            401 - если логин/email или пароль неверны
    """
    try:
        user = await authenticate_user(
            credentials.auth_param, credentials.password, credentials.methodAuth
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get(
    "",
    response_model=UserWithRelationsResponse,
    summary="Получить профиль текущего пользователя с связанными данными",
    responses={
        200: {"description": "Успешный запрос"},
        401: {"description": "Невалидный токен"},
        404: {"description": "Пользователь не найден"},
    },
)
async def get_user(
    current_user: User = Depends(get_current_user),  # api_key: str = Depends(validate_api_key)
):
    """
    Получает полную информацию о текущем пользователе и его связанных данных.

    Требует валидного JWT токена в заголовке Authorization.
    Возвращает данные пользователя и все связанные сущности (путешествия и др.).

    Args:
        current_user: Авторизованный пользователь (из токена)

    Returns:
        UserWithRelationsResponse: Полный профиль пользователя

    Example:
        Запрос:
        GET /me
        Authorization: Bearer eyJhbGciOi...

        Ответ:
        {
            "user": { ... },
            "travel": [ ... ],
        }
    """

    try:
        user_data = await PostgresUserDbClient.get_by_id_with_relations(user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting info user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )

    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User data not found")

    return user_data


@router.post(
    "/create",
    response_model=TokenResponse,
    summary="Создание пользователя",
    description="Создает пользователя и возвращает access_tokens",
    responses={
        200: {
            "description": "Успешная аутентификация",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "access_token": "eyJhbGciOi...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        400: {
            "description": "Ошибка запроса",
            "content": {
                "application/json": {"example": {"detail": "Invalid authentication method"}}
            },
        },
        500: {
            "description": "Внутрення ошибка сервера",
            "content": {"application/json": {"example": {"detail": "Incorrect data"}}},
        },
    },
)
async def create_user(credentials: UserRegister = Body(...)):


    hashed_password = get_password_hash(credentials.password)
    try:
        user = await PostgresUserDbClient.process(
            user_data={
                "login": credentials.login,
                "email": credentials.email,
                "hashed_password": hashed_password,
                "vkId": credentials.vkId,
            }
        )
    except UserAlreadyExistsError as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(success=True, access_token=access_token, token_type="bearer")


@router.patch(
    "/vkId/remove",
    response_model=SuccessResponse,
    summary="Отвязать vkId от аккаунта",
    responses={
        200: {"description": "Успешный запрос"},
        401: {"description": "Невалидный токен"},
        404: {"description": "Пользователь не найден"},
    },
)
async def remove_vkId(
    current_user: User = Depends(get_current_user),  # api_key: str = Depends(validate_api_key)
):
    """

    Args:
        current_user: Авторизованный пользователь (из токена)

    Returns:
        UserWithRelationsResponse: Полный профиль пользователя

    Example:
        Запрос:
        Patch /vkId/remove
        Authorization: Bearer eyJhbGciOi...

        Ответ:
        {
            "success": True,
            "detail": Какое-то сообщение
        }
    """

    if not getattr(current_user, "vk_id", None):
        return {"status_code": 200, "content": "vkId отсутствует"}

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User data not found")

    current_user.vk_id = None

    try:
        success = await PostgresUserDbClient.update(
            {   
                "id": current_user.id,
                "vk_id": current_user.vk_id,
            }
        )
    except Exception as e:
        logger.error(f"Error getting info user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )

    return {"status_code": 200, "content": "Токен успешно отвязан"}


@router.patch(
    "/vkId/add",
    response_model=SuccessResponse,
    summary="Привязать токен vkId к существующему пользователю",
    responses={
        200: {"description": "Успешный запрос"},
        401: {"description": "Невалидный токен"},
        404: {"description": "Пользователь не найден"},
    },
)
async def add_vkId(data: tokenAdd, current_user: User = Depends(get_current_user)):
    """

    Args:
        current_user: Авторизованный пользователь (из токена)

    Returns:
        UserWithRelationsResponse: Полный профиль пользователя

    Example:
        Запрос:
        Patch /vkId/add
        Authorization: Bearer eyJhbGciOi...

        Ответ:
        {
            "success": True,
            "detail": Какое-то сообщение
        }
    """

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User data not found")

    if getattr(current_user, "vk_id", None):
        return {"status_code": 200, "content": "vkId уже привязан"}

    try:
        success = await PostgresUserDbClient.update(
            {
                "id": current_user.id,
                "vk_id": data.token,
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=e
        )
    
    except UserAlreadyExistsError as e:
        logger.error(f"Error getting info user: {str(e)}")
        raise HTTPException(
            status_code=e.status_code, detail=e.message
        )


    return {"status_code": 200, "content": "Токен успешно привязаны"}


@router.patch(
    "/email/add",
    response_model=SuccessResponse,
    summary="Привязать email к существующему пользователю",
    responses={
        200: {"description": "Успешный запрос"},
        401: {"description": "Невалидный email"},
        404: {"description": "Пользователь не найден"},
    },
)
async def add_email(data: emailAdd, current_user: User = Depends(get_current_user) ):
    """

    Args:
        current_user: Авторизованный пользователь (из токена)

    Returns:
        { success: True, detail: message} OR HttpExeception

    Example:
        Запрос:
        Patch "/email/add"
        Authorization: Bearer eyJhbGciOi...
        Body: {
                "email": "email" 
                "password": "password"
        }

        Ответ:
        {
            "success": True,
            "detail": Какое-то сообщение
        }
    """

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    if getattr(current_user, "email", None):
        return {"status_code": 200, "content": "email уже привязан"}
    
    if not data.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не указан пароль")

    hashed_password = get_password_hash(data.password)
    
    try:
        success = await PostgresUserDbClient.update(
            {
                "id": current_user.id,
                "email": data.email,
                "hashed_password": hashed_password

            }
        )
    except ValueError as e:
        logger.warning(e)
        raise HTTPException(
            status_code=400, detail="Value error"
        )
    
    except UserAlreadyExistsError as e:
        logger.error(f"Error getting info user: {str(e)}")
        raise HTTPException(
            status_code=e.status_code, detail=e.message
        )


    return {"status_code": 200, "content": "Email успешно привязаны"}



@router.patch(
    "/email/update",
    response_model=SuccessResponse,
    summary="Обновить email у существующему пользователю",
    responses={
        200: {"description": "Успешный запрос"},
        401: {"description": "Невалидный email"},
        404: {"description": "Пользователь не найден"},
    },
)
async def update_email(data: emailUpdate, current_user: User = Depends(get_current_user)):
    """

    Args:
        current_user: Авторизованный пользователь (из токена)

    Returns:
        {success: True, detail: message} OR HttpExeception

    Example:
        Запрос:
        Patch "/email/update"
        Authorization: Bearer eyJhbGciOi...
        Body: {
                "email": "email" 
        }

        Ответ:
        {
            "success": True,
            "detail": Какое-то сообщение
        }
    """

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")


    try:
        success = await PostgresUserDbClient.update(
            {
                "id": current_user.id,
                "email": data.email
            }
        )
    except ValueError as e:
        
        raise HTTPException(
            status_code=400, detail=e
        )
    
    except UserAlreadyExistsError as e:
        logger.error(f"Error getting info user: {str(e)}")
        raise HTTPException(
            status_code=e.status_code, detail=e.message
        )


    return {"status_code": 200, "content": "Email успешно изменен"}