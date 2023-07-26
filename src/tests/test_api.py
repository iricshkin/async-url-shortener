from http import HTTPStatus

import pytest
from httpx import AsyncClient

from core.config import BLOCKED_IPS
from main import app


@pytest.mark.asyncio()
async def test_create_short_url(client: AsyncClient) -> None:
    response = await client.post(
        app.url_path_for('create_url'),
        json={'origin_url': 'http://ya.ru'},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert 'short_url' in response.json()


@pytest.mark.asyncio()
async def test_blocking(client: AsyncClient) -> None:
    BLOCKED_IPS.append('127.0.0.1')
    response = await client.post(
        app.url_path_for('create_url'),
        json={'origin_url': 'http://ya.ru'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio()
async def test_get_by_url_id(client: AsyncClient) -> None:
    post_response = await client.post(
        app.url_path_for('create_url'),
        json={'origin_url': 'http://ya.ru'},
    )
    url = post_response.json().get('short_url')
    get_response = await client.get(url)
    assert get_response.history[0].status_code == HTTPStatus.TEMPORARY_REDIRECT
    assert get_response.history[0].headers.get('Location') == 'http://ya.ru'


@pytest.mark.asyncio()
async def test_status(client: AsyncClient) -> None:
    post_response = await client.post(
        app.url_path_for('create_url'),
        json={'origin_url': 'http://ya.ru'},
    )
    url = post_response.json().get('short_url')
    await client.get(url)
    await client.get(url)
    status_response = await client.get(url + '/status')
    assert status_response.json().get('requests_number') == 2
    status_response_full = await client.get(
        url + '/status', params={'full-info': True}
    )
    results = status_response_full.json()
    assert len(results) == 2
    for result in results:
        assert result.get('made_at')
        assert result.get('client_host')
        assert result.get('client_port')
