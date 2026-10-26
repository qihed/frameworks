"""Подключение к базе данных SQLite проекта."""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "comics.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Создать соединение с базой данных и включить внешние ключи.

    По умолчанию SQLite не проверяет, что значение внешнего ключа
    ссылается на существующую запись другой таблицы, поэтому проверка
    включается командой PRAGMA для каждого соединения.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Создать таблицы по схеме sql/schema.sql (если их ещё нет)."""
    with open(SCHEMA_PATH, encoding="utf-8") as file:
        conn.executescript(file.read())
