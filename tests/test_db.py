"""Тесты слоя базы данных: схема, импорт из JSON и SQL-запросы."""

import json
import re
import sqlite3
from pathlib import Path

import pytest

from db import database
from db.import_json import COLLECTION_FILE, SERIES_FILE, USERS_FILE

QUERIES_FILE = Path("sql") / "queries.sql"


def _queries():
    """Разобрать sql/queries.sql на отдельные запросы."""
    lines = [
        line
        for line in QUERIES_FILE.read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("--")
    ]
    parts = "\n".join(lines).split(";")
    return [part.strip() for part in parts if part.strip()]


@pytest.fixture
def conn(sample_db):
    connection = database.get_connection()
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


def _count(path):
    return len(json.loads(Path(path).read_text(encoding="utf-8")))


def test_tables_are_created(conn):
    names = {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    assert {"series", "users", "collection_entries"} <= names


def test_foreign_keys_are_defined(conn):
    keys = conn.execute(
        "PRAGMA foreign_key_list(collection_entries)"
    ).fetchall()
    assert {(key["table"], key["from"]) for key in keys} == {
        ("series", "series_id"),
        ("users", "user_id"),
    }


def test_foreign_key_is_enforced(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO collection_entries "
            "(id, series_id, user_id) VALUES (?, ?, ?)",
            [100, 999, 1],
        )


def test_schema_can_be_applied_twice(conn):
    database.init_db(conn)
    database.init_db(conn)


def test_import_matches_json_files(conn):
    for table, path in (
        ("series", SERIES_FILE),
        ("users", USERS_FILE),
        ("collection_entries", COLLECTION_FILE),
    ):
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert count == _count(path)


def test_boolean_flag_is_stored_as_integer(conn):
    removed = conn.execute(
        "SELECT COUNT(*) FROM collection_entries WHERE is_removed = 1"
    ).fetchone()[0]
    assert removed == 1


def test_import_rolls_back_on_error(tmp_path, monkeypatch):
    from db.import_json import import_series

    broken = tmp_path / "series.json"
    broken.write_text(json.dumps([{"id": 1}]), encoding="utf-8")
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "x.sqlite")

    connection = database.get_connection()
    database.init_db(connection)
    with pytest.raises(KeyError):
        import_series(connection, broken)
    connection.close()


def test_queries_file_has_enough_queries_of_each_kind():
    queries = _queries()
    assert len(queries) >= 10

    def count(pattern):
        return sum(1 for q in queries if re.search(pattern, q, re.I))

    assert count(r"\bWHERE\b") >= 2
    assert count(r"\bJOIN\b") >= 2
    assert count(r"\b(COUNT|SUM|AVG|MIN|MAX)\(") >= 2
    assert count(r"\bGROUP BY\b") >= 2
    assert count(r"\bHAVING\b") >= 1
    assert count(r"^SELECT") == len(queries)


def test_every_query_executes(conn):
    for query in _queries():
        conn.execute(query, [1] * query.count("?")).fetchall()


def test_available_series_query(conn):
    rows = conn.execute(_query_by_title("Серии, доступные пользователю"),
                        [2, 2]).fetchall()
    assert [row["title"] for row in rows] == ["Watchmen"]


def test_active_readers_query(conn):
    rows = conn.execute(_query_by_title("Пользователи, прочитавшие больше"),
                        [30]).fetchall()
    assert [(row["user_name"], row["issues_read_total"]) for row in rows] == [
        ("Даниил", 43),
        ("Мария Смирнова", 39),
    ]


def test_entry_progress_query(conn):
    row = conn.execute(_query_by_title("Полная информация об одной записи"),
                       [1]).fetchone()
    assert row["progress"] == 41.3
    assert row["issues_left"] == 44


def test_left_join_keeps_series_without_entries(conn):
    conn.execute("UPDATE collection_entries SET is_removed = 1")
    rows = conn.execute(_query_by_title("Количество активных записей по")
                        ).fetchall()
    assert len(rows) == 6
    assert {row["entries_count"] for row in rows} == {0}


def _query_by_title(fragment):
    """Найти текст запроса по фрагменту комментария перед ним."""
    text = QUERIES_FILE.read_text(encoding="utf-8")
    blocks = re.split(r"(?m)^-- \d\.\d\. ", text)
    for block in blocks[1:]:
        title, _, rest = block.partition("\n")
        if fragment in title:
            body = [
                line for line in rest.split("\n")
                if not line.strip().startswith("--")
            ]
            return "\n".join(body).split(";")[0].strip()
    raise AssertionError(fragment)
