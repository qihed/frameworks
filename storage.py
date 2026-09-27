"""Функции сохранения и загрузки данных приложения в формате JSON."""

import json
from typing import List


def load_json_list(filename: str) -> List[dict]:
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


def save_json_list(filename: str, data: List[dict]) -> None:
    """Сохранить список словарей в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_series(filename: str) -> List[dict]:
    """Загрузить серии комиксов из JSON-файла."""
    return load_json_list(filename)


def save_series(filename: str, series_list: List[dict]) -> None:
    """Сохранить серии комиксов в JSON-файл."""
    save_json_list(filename, series_list)


def load_collection(filename: str) -> List[dict]:
    """Загрузить записи коллекции из JSON-файла."""
    return load_json_list(filename)


def save_collection(filename: str, collection: List[dict]) -> None:
    """Сохранить записи коллекции в JSON-файл."""
    save_json_list(filename, collection)
