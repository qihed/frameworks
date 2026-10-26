"""Представления страниц коллекции: данные получают SQL-запросы к SQLite."""

import sqlite3
from contextlib import closing

from django.shortcuts import render

from db.database import get_connection

# Порог числа прочитанных выпусков для списка «активных читателей».
ACTIVE_READER_THRESHOLD = 30


def collection_list(request):
    """Страница /collection/: активные записи (запрос 3.1)."""
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        entries = conn.execute("""
            SELECT
                collection_entries.id,
                collection_entries.status_code,
                collection_entries.issues_read,
                collection_entries.is_removed,
                series.title AS series_title,
                series.issues_total,
                users.name AS user_name
            FROM collection_entries
            JOIN series
                ON collection_entries.series_id = series.id
            JOIN users
                ON collection_entries.user_id = users.id
            WHERE collection_entries.is_removed = 0
            ORDER BY users.name, series.title;
        """).fetchall()

    return render(
        request,
        "collection/entry_list.html",
        {"entries": entries},
    )


def entry_detail(request, entry_id):
    """Страница /collection/<id>/: запись со связанными данными (3.2)."""
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        entry = conn.execute("""
            SELECT
                collection_entries.id,
                collection_entries.status_code,
                collection_entries.issues_read,
                collection_entries.is_removed,
                series.id AS series_id,
                series.title AS series_title,
                series.issues_total,
                users.name AS user_name,
                ROUND(
                    collection_entries.issues_read * 100.0
                    / series.issues_total,
                    1
                ) AS progress,
                MAX(
                    series.issues_total - collection_entries.issues_read,
                    0
                ) AS issues_left
            FROM collection_entries
            JOIN series
                ON collection_entries.series_id = series.id
            JOIN users
                ON collection_entries.user_id = users.id
            WHERE collection_entries.id = ?;
        """, [entry_id]).fetchone()

    return render(
        request,
        "collection/entry_detail.html",
        {"entry": entry},
        status=404 if entry is None else 200,
    )


def statistics(request):
    """Страница /collection/statistics/: статистика коллекции.

    Использует агрегатные функции, GROUP BY и HAVING
    (запросы 4.1, 4.2, 5.1, 5.2, 5.3, 5.4).
    """
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row

        entries_count = conn.execute("""
            SELECT
                COUNT(*) AS entries_count
            FROM collection_entries
            WHERE is_removed = 0;
        """).fetchone()["entries_count"]

        series_summary = conn.execute("""
            SELECT
                COUNT(*) AS series_count,
                SUM(issues_total) AS issues_sum,
                ROUND(AVG(issues_total), 1) AS issues_avg,
                MIN(issues_total) AS issues_min,
                MAX(issues_total) AS issues_max
            FROM series;
        """).fetchone()

        by_series = conn.execute("""
            SELECT
                series.title AS series_title,
                COUNT(collection_entries.id) AS entries_count
            FROM series
            LEFT JOIN collection_entries
                ON series.id = collection_entries.series_id
               AND collection_entries.is_removed = 0
            GROUP BY series.id, series.title
            ORDER BY entries_count DESC, series.title;
        """).fetchall()

        by_status = conn.execute("""
            SELECT
                status_code,
                CASE status_code
                    WHEN 1 THEN 'запланировано'
                    WHEN 2 THEN 'читаю'
                    WHEN 3 THEN 'прочитано'
                    WHEN 4 THEN 'брошено'
                    ELSE 'не определено'
                END AS status_name,
                COUNT(*) AS entries_count
            FROM collection_entries
            WHERE is_removed = 0
            GROUP BY status_code
            ORDER BY status_code;
        """).fetchall()

        by_user = conn.execute("""
            SELECT
                users.name AS user_name,
                COUNT(collection_entries.id) AS entries_count,
                COALESCE(
                    SUM(collection_entries.issues_read),
                    0
                ) AS issues_read_total
            FROM users
            LEFT JOIN collection_entries
                ON users.id = collection_entries.user_id
               AND collection_entries.is_removed = 0
            GROUP BY users.id, users.name
            ORDER BY issues_read_total DESC, users.name;
        """).fetchall()

        active_readers = conn.execute("""
            SELECT
                users.name AS user_name,
                SUM(collection_entries.issues_read) AS issues_read_total
            FROM users
            JOIN collection_entries
                ON users.id = collection_entries.user_id
            WHERE collection_entries.is_removed = 0
            GROUP BY users.id, users.name
            HAVING SUM(collection_entries.issues_read) > ?
            ORDER BY issues_read_total DESC;
        """, [ACTIVE_READER_THRESHOLD]).fetchall()

    context = {
        "entries_count": entries_count,
        "series_summary": series_summary,
        "by_series": by_series,
        "by_status": by_status,
        "by_user": by_user,
        "active_readers": active_readers,
        "threshold": ACTIVE_READER_THRESHOLD,
    }

    return render(request, "collection/statistics.html", context)
