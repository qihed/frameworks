"""Тесты веб-интерфейса: маршруты, коды ответа и содержимое страниц."""

import pytest
from django.test import Client, override_settings


@pytest.fixture
def client(sample_db):
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


def _template_names(response):
    return {template.name for template in response.templates}


@pytest.mark.parametrize(
    "url, template",
    [
        ("/", "homepage/index.html"),
        ("/series/", "series/series_list.html"),
        ("/series/1/", "series/series_detail.html"),
        ("/collection/", "collection/entry_list.html"),
        ("/collection/1/", "collection/entry_detail.html"),
    ],
)
def test_pages_use_templates_extending_base(client, url, template):
    names = _template_names(client.get(url))
    assert template in names
    assert "base.html" in names
    assert "includes/navigation.html" in names


def test_includes_are_used(client):
    assert "series/includes/series_card.html" in _template_names(
        client.get("/series/")
    )
    assert "collection/includes/entry_status.html" in _template_names(
        client.get("/collection/")
    )


def test_navigation_uses_named_urls(client):
    html = client.get("/").content.decode()
    for url in ("/", "/series/", "/collection/"):
        assert f'href="{url}"' in html


def test_filters_are_applied(client):
    assert "Всего серий: 6" in client.get("/series/").content.decode()
    assert "(41,3 %)" in client.get("/collection/1/").content.decode()
    assert "(100,0 %)" in client.get("/collection/3/").content.decode()


def test_entry_status_states(client):
    assert "Удалено" in client.get("/collection/7/").content.decode()
    assert "Читаю" in client.get("/collection/1/").content.decode()
    assert "Прочитано" in client.get("/collection/3/").content.decode()
    assert "Брошено" in client.get("/collection/5/").content.decode()


def test_missing_object_pages_show_message_in_template(client):
    series_page = client.get("/series/9999/")
    entry_page = client.get("/collection/9999/")
    assert "Серия не найдена" in series_page.content.decode()
    assert "Запись коллекции не найдена" in entry_page.content.decode()


def test_static_files_are_found():
    from django.contrib.staticfiles import finders

    for path in (
        "homepage/css/style.css",
        "homepage/js/main.js",
        "homepage/img/logo.png",
    ):
        assert finders.find(path), path


def test_base_template_loads_static_files(client):
    html = client.get("/").content.decode()
    assert "homepage/css/style.css" in html
    assert "homepage/js/main.js" in html
    assert "homepage/img/logo.png" in html


def test_views_do_not_use_page_function():
    from pathlib import Path

    for app in ("homepage", "series", "collection"):
        source = (Path(app) / "views.py").read_text(encoding="utf-8")
        assert "page(" not in source.replace("def page_not_found(", "")
        assert "HttpResponse" not in source


def test_available_series_form_without_user(client):
    html = client.get("/series/available/").content.decode()
    assert "Доступные серии" in html
    assert "Мария Смирнова" in html
    assert "Watchmen" not in html


def test_available_series_for_user(client):
    html = client.get("/series/available/?user=2").content.decode()
    assert "Watchmen" in html
    assert "Saga" not in html
    assert "Naruto" not in html


def test_available_series_without_matches(client, sample_db):
    import sqlite3

    connection = sqlite3.connect(sample_db)
    connection.execute(
        "INSERT INTO collection_entries (id, series_id, user_id) "
        "VALUES (100, 4, 2)"
    )
    connection.commit()
    connection.close()

    html = client.get("/series/available/?user=2").content.decode()
    assert "Подходящих серий нет" in html


@pytest.mark.parametrize("value", ["abc", "999"])
def test_available_series_invalid_user(client, value):
    response = client.get(f"/series/available/?user={value}")
    assert response.status_code == 200
    assert "text-danger" in response.content.decode()


def test_statistics_page(client):
    response = client.get("/collection/statistics/")
    html = response.content.decode()
    assert response.status_code == 200
    assert "Статистика коллекции" in html
    assert "Прочитали больше 30 выпусков" in html
    assert "Даниил" in html
    assert "collection/statistics.html" in _template_names(response)


def test_navigation_contains_statistics(client):
    html = client.get("/").content.decode()
    assert 'href="/collection/statistics/"' in html


def test_collection_list_shows_only_active_entries(client):
    html = client.get("/collection/").content.decode()
    assert "Активных записей: 6" in html
    assert "Удалено" not in html


def test_views_use_parameters_not_string_formatting():
    from pathlib import Path

    for app in ("series", "collection"):
        source = (Path(app) / "views.py").read_text(encoding="utf-8")
        assert 'execute(f"' not in source
        assert "execute(f'" not in source
        assert ".format(" not in source
