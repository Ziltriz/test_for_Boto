import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_shorten_url_success(client):
    """Успешное создание короткой ссылки"""
    response = client.post(
        "/shorten",
        json={"url": "https://example.com/very/long/path"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert "shorten_url" in data
    assert "original_url" in data
    assert data["original_url"] == "https://example.com/very/long/path"
    assert isinstance(data["shorten_url"], str)
    assert len(data["shorten_url"]) > 20


@pytest.mark.asyncio
async def test_shorten_invalid_url(client):
    """Попытка сократить невалидный URL"""
    response = client.post(
        "/shorten",
        json={"url": "not-a-url"}
    )
    
    assert response.status_code in (400, 422)
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_shorten_empty_payload(client):
    """POST без тела или с пустым url"""
    response = client.post("/shorten", json={})
    assert response.status_code in (400, 422)
    
    response = client.post("/shorten", json={"url": ""})
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_get_stats_existing_code(client):
    """Получаем статистику по существующему коду"""
    # Сначала создаём ссылку
    create_resp = client.post(
        "/shorten",
        json={"url": "https://test.com"}
    )
    assert create_resp.status_code == 201
    resp = create_resp.json()
    short_url = resp["shorten_url"]
    short_code = resp['code']
    
    # Теперь запрашиваем статистику
    stats_resp = client.get(f"/{short_code}")
    assert stats_resp.status_code == 200
    assert "text/html" in stats_resp.headers.get("content-type", "")
    
    content = stats_resp.text.lower()
    assert "перешли" in content or "click" in content or "раз" in content
    assert "https://test.com" in content


@pytest.mark.asyncio
async def test_get_stats_non_existing_code(client):
    """404 при запросе несуществующего кода"""
    response = client.get("/this-code-does-not-exist123")
    assert response.status_code == 404
    assert "не найдена" in response.text.lower() or "not found" in response.text.lower()


@pytest.mark.asyncio
async def test_multiple_clicks_increase_counter(client):
    """Счётчик кликов увеличивается при повторных просмотрах страницы"""
    # Создаём ссылку
    create_resp = client.post(
        "/shorten",
        json={"url": "https://counter.test"}
    )
    short_code = create_resp.json()["code"]
    client.get(f"/{short_code}")
    
    client.get(f"/{short_code}")
    
    stats_resp = client.get(f"/{short_code}")
    
    assert stats_resp.status_code == 200
    content = stats_resp.text.lower()
    assert "2" in content or "три" in content or "3" in content 