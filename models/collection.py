"""Класс CollectionEntry и функции работы с коллекцией пользователя.

Функция get_status_name() перенесена из начального сценария ПР1 без
изменения назначения.
"""

from typing import List, Optional

from .series import Series
from .users import User

STATUS_PLANNED = 1
STATUS_READING = 2
STATUS_FINISHED = 3
STATUS_DROPPED = 4

_STATUS_NAMES = {
    STATUS_PLANNED: "запланировано",
    STATUS_READING: "читаю",
    STATUS_FINISHED: "прочитано",
    STATUS_DROPPED: "брошено",
}


def get_status_name(status_code: int) -> str:
    """Вернуть читаемое название состояния чтения серии по его коду."""
    return _STATUS_NAMES.get(status_code, "состояние не определено")


class CollectionEntry:
    """Запись пользовательской коллекции: серия, отслеживаемая пользователем."""

    def __init__(
        self,
        entry_id: int,
        series: Series,
        user: User,
        status_code: int = STATUS_PLANNED,
        issues_read: int = 0,
    ) -> None:
        """Создать запись коллекции, связав её с серией и пользователем."""
        self.id = entry_id
        self.series = series
        self.user = user
        self.status_code = status_code
        self.issues_read = issues_read
        self.is_removed = False

    def remove(self) -> None:
        """Пометить запись как удалённую из коллекции."""
        self.is_removed = True

    def calculate_progress(self) -> float:
        """Рассчитать прогресс чтения серии в процентах."""
        if self.series.issues_total <= 0:
            return 0.0
        issues_read = min(self.issues_read, self.series.issues_total)
        return issues_read / self.series.issues_total * 100

    def count_issues_left(self) -> int:
        """Посчитать, сколько выпусков серии осталось прочитать."""
        if self.issues_read >= self.series.issues_total:
            return 0
        return self.series.issues_total - self.issues_read

    @property
    def status(self) -> str:
        """Вернуть текстовый статус записи с учётом её удаления."""
        if self.is_removed:
            return "удалено из коллекции"
        return get_status_name(self.status_code)

    def __str__(self) -> str:
        """Вернуть строковое представление записи коллекции."""
        progress = self.calculate_progress()
        return (
            f"{self.series.title} ({self.user.name}) — {self.status}, "
            f"прогресс {round(progress, 1)} % "
            f"({self.issues_read}/{self.series.issues_total})"
        )


def is_series_in_collection(
    collection: List[CollectionEntry],
    series: Series,
) -> bool:
    """Проверить, есть ли в коллекции активная запись по серии."""
    for entry in collection:
        if entry.series.id == series.id and not entry.is_removed:
            return True
    return False


def get_collection_status(is_available: bool) -> str:
    """Вернуть текстовое сообщение о доступности серии для добавления."""
    if is_available:
        return "Серию можно добавить в коллекцию"
    return "Серия уже находится в коллекции"


def add_to_collection(
    collection: List[CollectionEntry],
    series: Series,
    user: User,
    status_code: int = STATUS_PLANNED,
) -> Optional[CollectionEntry]:
    """Создать запись коллекции для серии и пользователя, если это возможно.

    Возвращает None, если серия уже находится в активной коллекции
    пользователя или недоступна ему по возрасту.
    """
    already_in_collection = is_series_in_collection(collection, series)
    if already_in_collection or not series.is_suitable_for(user.age):
        return None
    new_id = max((entry.id for entry in collection), default=0) + 1
    entry = CollectionEntry(new_id, series, user, status_code)
    collection.append(entry)
    return entry


def find_entry_by_id(
    collection: List[CollectionEntry],
    entry_id: int,
) -> Optional[CollectionEntry]:
    """Найти запись коллекции по идентификатору."""
    for entry in collection:
        if entry.id == entry_id:
            return entry
    return None


def remove_from_collection(
    collection: List[CollectionEntry],
    entry_id: int,
) -> bool:
    """Найти запись коллекции по идентификатору и вызвать её remove()."""
    entry = find_entry_by_id(collection, entry_id)
    if entry is None:
        return False
    entry.remove()
    return True


def update_issues_read(
    collection: List[CollectionEntry],
    entry_id: int,
    issues_read: int,
) -> bool:
    """Обновить количество прочитанных выпусков в записи коллекции."""
    entry = find_entry_by_id(collection, entry_id)
    if entry is None:
        return False
    entry.issues_read = issues_read
    return True


def show_collection(collection: List[CollectionEntry]) -> None:
    """Вывести список записей коллекции."""
    if not collection:
        print("Коллекция пуста.")
        return
    for entry in collection:
        print(f"[{entry.id}] {entry}")
