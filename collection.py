"""Функции для работы с записями пользовательской коллекции комиксов.

Часть функций (get_status_name, can_add_to_collection, calculate_progress,
count_issues_left) перенесена из начального сценария ПР1 без изменения
их назначения и адаптирована для работы с коллекциями.
"""

from typing import List, Optional

from series import find_series_by_id

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


def is_series_in_collection(collection: List[dict], series_id: int) -> bool:
    """Проверить, есть ли в коллекции активная запись по серии."""
    for entry in collection:
        if entry["series_id"] == series_id and not entry["is_removed"]:
            return True
    return False


def can_add_to_collection(
    is_in_collection: bool,
    user_age: int,
    age_limit: int,
) -> bool:
    """Проверить, можно ли добавить серию в коллекцию пользователя.

    Серию можно добавить, если её ещё нет в активной коллекции
    и возраст пользователя не меньше возрастного ограничения серии.
    """
    return not is_in_collection and user_age >= age_limit


def get_collection_status(is_available: bool) -> str:
    """Вернуть текстовый статус доступности серии для добавления."""
    if is_available:
        return "Серию можно добавить в коллекцию"
    return "Серия уже находится в коллекции"


def add_to_collection(
    collection: List[dict],
    series_list: List[dict],
    series_id: int,
    user_age: int,
    status_code: int = STATUS_PLANNED,
) -> Optional[dict]:
    """Создать запись коллекции для указанной серии, если это возможно.

    Возвращает None, если серия не найдена, уже находится в активной
    коллекции или недоступна пользователю по возрасту.
    """
    series = find_series_by_id(series_list, series_id)
    if series is None:
        return None
    already_in_collection = is_series_in_collection(collection, series_id)
    if not can_add_to_collection(
        already_in_collection, user_age, series["age_limit"]
    ):
        return None
    new_id = max((entry["id"] for entry in collection), default=0) + 1
    entry = {
        "id": new_id,
        "series_id": series_id,
        "status_code": status_code,
        "issues_read": 0,
        "is_removed": False,
    }
    collection.append(entry)
    return entry


def remove_from_collection(collection: List[dict], entry_id: int) -> bool:
    """Отметить запись коллекции как удалённую, не удаляя её из списка."""
    for entry in collection:
        if entry["id"] == entry_id:
            entry["is_removed"] = True
            return True
    return False


def update_issues_read(
    collection: List[dict],
    entry_id: int,
    issues_read: int,
) -> bool:
    """Обновить количество прочитанных выпусков в записи коллекции."""
    for entry in collection:
        if entry["id"] == entry_id:
            entry["issues_read"] = issues_read
            return True
    return False


def calculate_progress(issues_read: int, issues_total: int) -> float:
    """Рассчитать прогресс чтения серии в процентах."""
    if issues_total <= 0:
        return 0.0
    if issues_read > issues_total:
        issues_read = issues_total
    return issues_read / issues_total * 100


def count_issues_left(issues_read: int, issues_total: int) -> int:
    """Посчитать, сколько выпусков серии осталось прочитать."""
    if issues_read >= issues_total:
        return 0
    return issues_total - issues_read


def format_collection_entry(entry: dict, series_list: List[dict]) -> str:
    """Собрать карточку записи коллекции для вывода пользователю."""
    series = find_series_by_id(series_list, entry["series_id"])
    if series is None:
        return f"[{entry['id']}] серия не найдена"
    status_name = get_status_name(entry["status_code"])
    progress = calculate_progress(entry["issues_read"], series["issues_total"])
    removed_mark = " (удалено из коллекции)" if entry["is_removed"] else ""
    return (
        f"[{entry['id']}] {series['title']} — {status_name}, "
        f"прогресс {round(progress, 1)} % "
        f"({entry['issues_read']}/{series['issues_total']}){removed_mark}"
    )


def show_collection(collection: List[dict], series_list: List[dict]) -> None:
    """Вывести список записей коллекции."""
    if not collection:
        print("Коллекция пуста.")
        return
    for entry in collection:
        print(format_collection_entry(entry, series_list))
