"""Класс Series и функции работы с коллекцией серий комиксов."""

from typing import List, Optional


class Series:
    """Серия комиксов, доступная для добавления в коллекцию."""

    def __init__(
        self,
        series_id: int,
        title: str,
        publisher: str,
        author: str,
        issues_total: int,
        age_limit: int,
    ) -> None:
        """Создать объект серии."""
        self.id = series_id
        self.title = title
        self.publisher = publisher
        self.author = author
        self.issues_total = issues_total
        self.age_limit = age_limit

    def is_suitable_for(self, user_age: int) -> bool:
        """Проверить, доступна ли серия пользователю по возрасту."""
        return user_age >= self.age_limit

    @staticmethod
    def validate_age_limit(age_limit: int) -> bool:
        """Проверить корректность значения возрастного ограничения."""
        return age_limit >= 0

    def __str__(self) -> str:
        """Вернуть строковое представление серии."""
        return (
            f"{self.title} — {self.publisher}, автор {self.author}, "
            f"выпусков: {self.issues_total}, {self.age_limit}+"
        )


def add_series(
    series_list: List[Series],
    title: str,
    publisher: str,
    author: str,
    issues_total: int,
    age_limit: int,
) -> Series:
    """Создать объект Series, добавить его в коллекцию и вернуть."""
    new_id = max((series.id for series in series_list), default=0) + 1
    series = Series(new_id, title, publisher, author, issues_total, age_limit)
    series_list.append(series)
    return series


def find_series_by_id(
    series_list: List[Series],
    series_id: int,
) -> Optional[Series]:
    """Найти серию по идентификатору."""
    for series in series_list:
        if series.id == series_id:
            return series
    return None


def find_series(series_list: List[Series], query: str) -> List[Series]:
    """Найти серии, в названии которых встречается подстрока query."""
    query_lower = query.lower()
    return [
        series for series in series_list
        if query_lower in series.title.lower()
    ]


def check_series_age_limit(
    series_list: List[Series],
    series_id: int,
    user_age: int,
) -> bool:
    """Проверить, доступна ли серия пользователю по возрасту."""
    series = find_series_by_id(series_list, series_id)
    if series is None:
        return False
    return series.is_suitable_for(user_age)


def filter_series_by_age_limit(
    series_list: List[Series],
    max_age_limit: int,
) -> List[Series]:
    """Отобрать серии с возрастным ограничением не выше указанного."""
    return [series for series in series_list if series.age_limit <= max_age_limit]


def sort_series_by_issues(
    series_list: List[Series],
    reverse: bool = False,
) -> List[Series]:
    """Отсортировать серии по количеству выпусков."""
    return sorted(
        series_list, key=lambda series: series.issues_total, reverse=reverse
    )


def show_series(series_list: List[Series]) -> None:
    """Вывести список серий."""
    if not series_list:
        print("Список серий пуст.")
        return
    for series in series_list:
        print(f"[{series.id}] {series}")
