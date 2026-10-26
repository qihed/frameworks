"""Тесты веб-интерфейса: маршруты, коды ответа и содержимое страниц."""

import pytest
from django.test import Client, override_settings


@pytest.fixture
def client():
    return Client()


@pytest.mark.parametrize(
    "url, text",
    [
        ("/", "Сервис учёта комиксов"),
        ("/series/", "The Sandman"),
        ("/series/1/", "Neil Gaiman"),
        ("/collection/", "Даниил"),
        ("/collection/1/", "Запись коллекции №1"),
    ],
)
def test_pages_open(client, url, text):
    response = client.get(url)
    assert response.status_code == 200
    assert text in response.content.decode()


@pytest.mark.parametrize("url", ["/series/9999/", "/collection/9999/"])
def test_missing_objects_return_404(client, url):
    assert client.get(url).status_code == 404


def test_series_detail_shows_collection_state(client):
    assert "в коллекции" in client.get("/series/1/").content.decode()


def test_non_int_id_is_not_routed(client):
    assert client.get("/series/abc/").status_code == 404


def test_custom_404_page_without_debug(client):
    with override_settings(DEBUG=False):
        response = client.get("/nonexistent/")
    assert response.status_code == 404
    assert "404 – страница не найдена" in response.content.decode()
