"""Сервис учёта комиксов.

Индивидуальный сквозной проект, практическая работа № 2.

Начальный сценарий ПР1 (простые переменные, одна функция форматирования
статуса) переработан: данные серий и записей коллекции переведены в
коллекции словарей, логика распределена между модулями series.py
(серии комиксов) и collection.py (записи пользовательской коллекции),
добавлены хранение данных в JSON-файлах, обработка исключений и
разбиение программы на модули.
"""

from typing import List

from collection import (
    STATUS_PLANNED,
    STATUS_READING,
    add_to_collection,
    get_collection_status,
    is_series_in_collection,
    remove_from_collection,
    show_collection,
    update_issues_read,
)
from series import (
    add_series,
    check_series_age_limit,
    filter_series_by_age_limit,
    find_series,
    find_series_by_id,
    show_series,
    sort_series_by_issues,
)
from storage import load_collection, load_series, save_collection, save_series
from utils import input_int, input_nonempty_str

SERIES_FILE = "data/series.json"
COLLECTION_FILE = "data/collection.json"

MENU = """
=== Сервис учёта комиксов ===
1. Показать серии
2. Найти серию по названию
3. Проверить возрастной доступ к серии
4. Добавить новую серию
5. Показать серии с ограничением не старше заданного
6. Показать коллекцию
7. Добавить серию в коллекцию
8. Обновить количество прочитанных выпусков
9. Удалить серию из коллекции
0. Выход
"""


def seed_initial_data() -> tuple:
    """Сформировать исходные данные на основе сценария ПР1.

    Используется, если файлы данных отсутствуют: сохраняет пример
    из начального сценария (серия The Sandman, статус "читаю").
    """
    series_list = [
        {
            "id": 1,
            "title": "The Sandman",
            "publisher": "DC Comics",
            "author": "Neil Gaiman",
            "issues_total": 75,
            "age_limit": 18,
        }
    ]
    collection = [
        {
            "id": 1,
            "series_id": 1,
            "status_code": STATUS_READING,
            "issues_read": 31,
            "is_removed": False,
        }
    ]
    return series_list, collection


def create_new_series(series_list: List[dict]) -> None:
    """Добавить новую серию по данным, введённым пользователем."""
    title = input_nonempty_str("Название серии: ")
    publisher = input_nonempty_str("Издатель: ")
    author = input_nonempty_str("Автор: ")
    issues_total = input_int("Всего выпусков в серии: ")
    age_limit = input_int("Возрастное ограничение: ")
    series = add_series(
        series_list, title, publisher, author, issues_total, age_limit
    )
    print(f"Добавлена серия с идентификатором {series['id']}.")


def create_new_collection_entry(
    collection: List[dict],
    series_list: List[dict],
    user_age: int,
) -> None:
    """Выполнить пользовательский сценарий добавления серии в коллекцию."""
    series_id = input_int("Идентификатор серии: ")
    series = find_series_by_id(series_list, series_id)
    if series is None:
        print("Серия с таким идентификатором не найдена.")
        return

    already_in_collection = is_series_in_collection(collection, series_id)
    is_available = not already_in_collection and user_age >= series["age_limit"]
    print(get_collection_status(is_available))

    entry = add_to_collection(
        collection, series_list, series_id, user_age, STATUS_PLANNED
    )
    if entry is None:
        if not already_in_collection:
            print(
                "Операция отменена: возрастное ограничение "
                f"{series['age_limit']}+, ваш возраст — {user_age}."
            )
        return
    print(f"Серия добавлена в коллекцию, идентификатор записи {entry['id']}.")


def update_collection_progress(collection: List[dict]) -> None:
    """Выполнить пользовательский сценарий обновления прогресса чтения."""
    entry_id = input_int("Идентификатор записи коллекции: ")
    issues_read = input_int("Прочитано выпусков: ")
    if update_issues_read(collection, entry_id, issues_read):
        print("Прогресс обновлён.")
    else:
        print("Запись коллекции с таким идентификатором не найдена.")


def remove_collection_entry(collection: List[dict]) -> None:
    """Выполнить пользовательский сценарий удаления записи коллекции."""
    entry_id = input_int("Идентификатор записи коллекции: ")
    if remove_from_collection(collection, entry_id):
        print("Запись удалена из коллекции.")
    else:
        print("Запись коллекции с таким идентификатором не найдена.")


def main() -> None:
    """Точка запуска приложения: главное меню и работа с данными."""
    series_list = load_series(SERIES_FILE)
    collection = load_collection(COLLECTION_FILE)
    if not series_list and not collection:
        series_list, collection = seed_initial_data()

    user_age = input_int("Ваш возраст: ")

    while True:
        print(MENU)
        choice = input_int("Выберите действие: ")

        if choice == 1:
            show_series(series_list)
        elif choice == 2:
            query = input_nonempty_str("Подстрока названия: ")
            show_series(find_series(series_list, query))
        elif choice == 3:
            series_id = input_int("Идентификатор серии: ")
            if check_series_age_limit(series_list, series_id, user_age):
                print("Серия доступна по возрасту.")
            else:
                print("Серия недоступна по возрасту или не найдена.")
        elif choice == 4:
            create_new_series(series_list)
        elif choice == 5:
            max_age_limit = input_int("Показать серии не старше: ")
            show_series(filter_series_by_age_limit(series_list, max_age_limit))
        elif choice == 6:
            show_collection(collection, series_list)
        elif choice == 7:
            create_new_collection_entry(collection, series_list, user_age)
        elif choice == 8:
            update_collection_progress(collection)
        elif choice == 9:
            remove_collection_entry(collection)
        elif choice == 0:
            save_series(SERIES_FILE, series_list)
            save_collection(COLLECTION_FILE, collection)
            print("Данные сохранены. До встречи!")
            break
        else:
            print("Неизвестный пункт меню.")

    sorted_by_issues = sort_series_by_issues(series_list)
    if sorted_by_issues:
        shortest = sorted_by_issues[0]
        print(f"Самая короткая серия в базе: {shortest['title']}.")


if __name__ == "__main__":
    main()
