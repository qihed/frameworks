"""Функции сохранения и загрузки данных приложения в формате JSON.

Выполняет преобразование JSON -> объекты Python при загрузке и
объекты Python -> JSON при сохранении. Связи между объектами
(CollectionEntry -> Series, CollectionEntry -> User) при сохранении
заменяются идентификаторами, а при загрузке восстанавливаются поиском
объектов в уже загруженных коллекциях.
"""

import json
from typing import List

from models import CollectionEntry, Series, User
from models.series import find_series_by_id
from models.users import find_user_by_id


def _load_raw_list(filename: str) -> list:
    """Загрузить список словарей из JSON-файла.

    Если файл отсутствует или содержит повреждённые данные,
    возвращается пустой список, а программа не завершается аварийно.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Файл {filename} повреждён, будет использован пустой список.")
        return []
    if not isinstance(data, list):
        return []
    return data


def _save_raw_list(filename: str, data: list) -> None:
    """Сохранить список словарей в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_series(filename: str) -> List[Series]:
    """Загрузить серии из JSON-файла и создать объекты Series."""
    raw_items = _load_raw_list(filename)
    return [
        Series(
            item["id"],
            item["title"],
            item["publisher"],
            item["author"],
            item["issues_total"],
            item["age_limit"],
        )
        for item in raw_items
    ]


def save_series(filename: str, series_list: List[Series]) -> None:
    """Сохранить объекты Series в JSON-файл."""
    data = [
        {
            "id": series.id,
            "title": series.title,
            "publisher": series.publisher,
            "author": series.author,
            "issues_total": series.issues_total,
            "age_limit": series.age_limit,
        }
        for series in series_list
    ]
    _save_raw_list(filename, data)


def load_users(filename: str) -> List[User]:
    """Загрузить пользователей из JSON-файла и создать объекты User."""
    raw_items = _load_raw_list(filename)
    return [User.from_data(item) for item in raw_items]


def save_users(filename: str, users: List[User]) -> None:
    """Сохранить объекты User в JSON-файл."""
    data = [
        {
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "email": user.email,
        }
        for user in users
    ]
    _save_raw_list(filename, data)


def load_collection(
    filename: str,
    series_list: List[Series],
    users: List[User],
) -> List[CollectionEntry]:
    """Загрузить записи коллекции, восстановив связи с Series и User.

    Запись, ссылающаяся на отсутствующую серию или пользователя,
    пропускается, чтобы не создавать некорректный объект.
    """
    raw_items = _load_raw_list(filename)
    collection: List[CollectionEntry] = []
    for item in raw_items:
        series = find_series_by_id(series_list, item["series_id"])
        user = find_user_by_id(users, item["user_id"])
        if series is None or user is None:
            continue
        entry = CollectionEntry(
            item["id"],
            series,
            user,
            item["status_code"],
            item["issues_read"],
        )
        entry.is_removed = item["is_removed"]
        collection.append(entry)
    return collection


def save_collection(filename: str, collection: List[CollectionEntry]) -> None:
    """Сохранить записи коллекции, заменив ссылки на объекты их id."""
    data = [
        {
            "id": entry.id,
            "series_id": entry.series.id,
            "user_id": entry.user.id,
            "status_code": entry.status_code,
            "issues_read": entry.issues_read,
            "is_removed": entry.is_removed,
        }
        for entry in collection
    ]
    _save_raw_list(filename, data)
