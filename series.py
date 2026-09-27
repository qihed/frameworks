"""Функции для работы с сериями комиксов, доступными для учёта."""

from typing import List, Optional


def add_series(
    series_list: List[dict],
    title: str,
    publisher: str,
    author: str,
    issues_total: int,
    age_limit: int,
) -> dict:
    """Добавить серию в коллекцию доступных серий и вернуть её данные."""
    new_id = max((item["id"] for item in series_list), default=0) + 1
    new_series = {
        "id": new_id,
        "title": title,
        "publisher": publisher,
        "author": author,
        "issues_total": issues_total,
        "age_limit": age_limit,
    }
    series_list.append(new_series)
    return new_series


def find_series_by_id(series_list: List[dict], series_id: int) -> Optional[dict]:
    """Найти серию по идентификатору."""
    for series in series_list:
        if series["id"] == series_id:
            return series
    return None


def find_series(series_list: List[dict], query: str) -> List[dict]:
    """Найти серии, в названии которых встречается подстрока query."""
    query_lower = query.lower()
    return [
        series for series in series_list
        if query_lower in series["title"].lower()
    ]


def check_series_age_limit(
    series_list: List[dict],
    series_id: int,
    user_age: int,
) -> bool:
    """Проверить, доступна ли серия пользователю по возрасту."""
    series = find_series_by_id(series_list, series_id)
    if series is None:
        return False
    return user_age >= series["age_limit"]


def filter_series_by_age_limit(
    series_list: List[dict],
    max_age_limit: int,
) -> List[dict]:
    """Отобрать серии с возрастным ограничением не выше указанного."""
    return [
        series for series in series_list
        if series["age_limit"] <= max_age_limit
    ]


def sort_series_by_issues(
    series_list: List[dict],
    reverse: bool = False,
) -> List[dict]:
    """Отсортировать серии по количеству выпусков."""
    return sorted(
        series_list,
        key=lambda series: series["issues_total"],
        reverse=reverse,
    )


def show_series(series_list: List[dict]) -> None:
    """Вывести список серий."""
    if not series_list:
        print("Список серий пуст.")
        return
    for series in series_list:
        print(
            f"[{series['id']}] {series['title']} — {series['publisher']}, "
            f"автор {series['author']}, выпусков: {series['issues_total']}, "
            f"{series['age_limit']}+"
        )
