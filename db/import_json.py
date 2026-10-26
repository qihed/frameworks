"""Однократный перенос данных проекта из JSON-файлов в SQLite."""

import json
import sqlite3

from db.database import BASE_DIR, get_connection, init_db

DATA_DIR = BASE_DIR / "data"
SERIES_FILE = DATA_DIR / "series.json"
USERS_FILE = DATA_DIR / "users.json"
COLLECTION_FILE = DATA_DIR / "collection.json"


def load_json(filename) -> list:
    """Прочитать JSON-файл и вернуть его содержимое."""
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def import_series(conn: sqlite3.Connection, filename=SERIES_FILE) -> None:
    """Перенести серии из JSON в таблицу series."""
    series_items = load_json(filename)
    conn.executemany(
        """
        INSERT INTO series (
            id,
            title,
            publisher,
            author,
            issues_total,
            age_limit
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                series["id"],
                series["title"],
                series["publisher"],
                series["author"],
                series["issues_total"],
                series["age_limit"],
            )
            for series in series_items
        ],
    )


def import_users(conn: sqlite3.Connection, filename=USERS_FILE) -> None:
    """Перенести пользователей из JSON в таблицу users."""
    users = load_json(filename)
    conn.executemany(
        """
        INSERT INTO users (
            id,
            name,
            age,
            email
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                user["id"],
                user["name"],
                user["age"],
                user["email"],
            )
            for user in users
        ],
    )


def import_collection(
    conn: sqlite3.Connection,
    filename=COLLECTION_FILE,
) -> None:
    """Перенести записи коллекции из JSON в таблицу collection_entries."""
    entries = load_json(filename)
    conn.executemany(
        """
        INSERT INTO collection_entries (
            id,
            series_id,
            user_id,
            status_code,
            issues_read,
            is_removed
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                entry["id"],
                entry["series_id"],
                entry["user_id"],
                entry["status_code"],
                entry["issues_read"],
                int(entry["is_removed"]),
            )
            for entry in entries
        ],
    )


def import_all(conn: sqlite3.Connection) -> None:
    """Выполнить перенос всех данных в порядке, учитывающем связи.

    Сначала переносятся таблицы, на которые ссылаются внешние ключи
    (series, users), затем зависящая от них collection_entries.
    """
    import_series(conn)
    import_users(conn)
    import_collection(conn)


def main() -> None:
    """Создать таблицы (если нужно) и перенести данные одной транзакцией."""
    conn = get_connection()
    try:
        init_db(conn)
        import_all(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
