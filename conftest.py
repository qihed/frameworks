"""Корневой conftest.py.

Наличие файла в корне проекта обеспечивает добавление корня проекта
в sys.path при запуске pytest, что позволяет тестам импортировать
модули приложения (models, storage, utils и т. д.) без установки
проекта как пакета. Дополнительно инициализируется Django, чтобы
тесты веб-интерфейса могли пользоваться тестовым клиентом.
"""

import os

import django
import pytest
from django.test.utils import setup_test_environment

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comicstracker.settings")
django.setup()
setup_test_environment()


@pytest.fixture
def sample_db(tmp_path, monkeypatch):
    """Временная база SQLite, заполненная данными из data/*.json.

    Путь к базе подменяется в db.database, поэтому представления и
    тесты работают с копией, а не с файлом data/comics.sqlite.
    """
    from db import database
    from db.import_json import import_all

    path = tmp_path / "test_comics.sqlite"
    monkeypatch.setattr(database, "DB_PATH", path)

    conn = database.get_connection()
    database.init_db(conn)
    import_all(conn)
    conn.commit()
    conn.close()
    return path
