"""Представления страниц серий: данные получаются SQL-запросами к SQLite."""

import sqlite3
from contextlib import closing

from django.shortcuts import render

from db.database import get_connection


def series_list(request):
    """Страница /series/: список серий (запрос 1.1 из sql/queries.sql)."""
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        series_items = conn.execute("""
            SELECT
                id,
                title,
                publisher,
                author,
                issues_total,
                age_limit
            FROM series
            ORDER BY title;
        """).fetchall()

    return render(
        request,
        "series/series_list.html",
        {"series_items": series_items},
    )


def series_detail(request, series_id):
    """Страница /series/<id>/: карточка серии (запросы 6.1 и 6.2)."""
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        series = conn.execute("""
            SELECT
                id,
                title,
                publisher,
                author,
                issues_total,
                age_limit
            FROM series
            WHERE id = ?;
        """, [series_id]).fetchone()

        entries_count = conn.execute("""
            SELECT
                COUNT(*) AS entries_count
            FROM collection_entries
            WHERE series_id = ?
              AND is_removed = 0;
        """, [series_id]).fetchone()["entries_count"]

    context = {
        "series": series,
        "in_collection": entries_count > 0,
    }

    return render(
        request,
        "series/series_detail.html",
        context,
        status=404 if series is None else 200,
    )


def available_series(request):
    """Страница /series/available/: серии, доступные пользователю.

    Серия доступна, если подходит пользователю по возрасту и ещё не
    добавлена им в активную коллекцию (запрос 2.4). Идентификатор
    пользователя передаётся параметром ?user=<id>.
    """
    user_id = request.GET.get("user", "")
    series_items = []
    selected_user = None
    error = ""

    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        users = conn.execute("""
            SELECT
                id,
                name,
                age,
                email
            FROM users
            ORDER BY name;
        """).fetchall()

        if user_id:
            if not user_id.isdigit():
                error = "Идентификатор пользователя должен быть числом."
            else:
                selected_user = conn.execute(
                    "SELECT id, name, age FROM users WHERE id = ?;",
                    [int(user_id)],
                ).fetchone()
                if selected_user is None:
                    error = "Пользователь с таким идентификатором не найден."

        if selected_user is not None:
            series_items = conn.execute("""
                SELECT
                    series.id,
                    series.title,
                    series.publisher,
                    series.author,
                    series.issues_total,
                    series.age_limit
                FROM series
                WHERE series.age_limit <= (
                        SELECT users.age
                        FROM users
                        WHERE users.id = ?
                    )
                  AND series.id NOT IN (
                        SELECT collection_entries.series_id
                        FROM collection_entries
                        WHERE collection_entries.user_id = ?
                          AND collection_entries.is_removed = 0
                    )
                ORDER BY series.title;
            """, [selected_user["id"], selected_user["id"]]).fetchall()

    context = {
        "users": users,
        "selected_user": selected_user,
        "series_items": series_items,
        "error": error,
    }

    return render(request, "series/available.html", context)
