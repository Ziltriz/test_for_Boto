from fastapi import HTTPException, APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.schemas.request import ShortenRequest
from src.schemas.response import ErrorResponse, ShortenResponse
from src.db.clients.lite_client import UrlInfoDbClient
from src.utils.generators import generate_short_code, get_base_url
from pathlib import Path

from src.core.log_manager import LogManager


router = APIRouter()


parent_directory = Path(__file__).parent.parent
templates_path = parent_directory.parent / "templates"
templates = Jinja2Templates(directory=templates_path)


@router.post(
        "/shorten",
        response_model=ShortenResponse,
        summary="Сокращает полученную ссылку",
        status_code= status.HTTP_201_CREATED,
        responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
        tags=["Shorten"]
    )
async def shorten_url(
    payload: ShortenRequest, 
    request: Request,
):
    LogManager.sync_log_network_info("/shorten", "Полученн запрос на сокращение", {"payload": payload})
    original_url_str = str(payload.url)
    exists_url = UrlInfoDbClient.get_by_id(original_url_str)
    
    if exists_url:
        UrlInfoDbClient.increment_clicks(exists_url.original_url)
        short_url = exists_url.short_url
        short_code = exists_url.short_code

    else:
        base_url = get_base_url(request)
        short_code = generate_short_code()
        short_url = base_url+"/"+short_code+"_byzil"
        data = {
            'short_url': short_url,
            'short_code': short_code,
            'original_url': original_url_str,
            'clicks': 0,
        }
       

        try:
            result = UrlInfoDbClient.process(data)

        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"{e}")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred. Report this message to support: {e}",
            )
    
    return ShortenResponse(
        shorten_url=short_url,
        code=short_code,
        original_url=original_url_str
    )


@router.get("/{short_code}", response_class=HTMLResponse)
async def show_link_stats(request: Request, short_code: str):
    """
    Показывает простую HTML-страницу со статистикой кликов
    вместо автоматического редиректа
    """
    record = UrlInfoDbClient.get_by_id(str(request.url), short_code)
    
    if not record:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    UrlInfoDbClient.increment_clicks(record.original_url)

    # логируем просмотр статистики
    await LogManager.log_network_info(
        endpoint=f"/{short_code}",
        message="Просмотр статистики ссылки",
        data={"short_code": short_code, "clicks": record.clicks+1}
    )

    return templates.TemplateResponse(
        "link_stats.html",
        {
            "request": request,
            "short_code": short_code,
            "original_url": record.original_url,
            "clicks": record.clicks+1,
            "created_at": record.created_at,
        }
    )