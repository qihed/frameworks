"""Сервис учёта комиксов.

Индивидуальный сквозной проект, практическая работа № 3.

Функциональная модель ПР2 (словари, отдельные функции обработки)
переработана в объектно-ориентированную: серии, пользователи и записи
коллекции представлены классами Series, User и CollectionEntry из
пакета models. main.py не хранит словари предметной области — только
коллекции объектов, которые передаются в функции модулей models.*.
"""

from typing import List, Optional

from decorators import log_action
from models import CollectionEntry, Series, User
from models.collection import (
    STATUS_PLANNED,
    STATUS_READING,
    add_to_collection,
    get_collection_status,
    is_series_in_collection,
    remove_from_collection,
    show_collection,
    update_issues_read,
)
from models.series import (
    add_series,
    check_series_age_limit,
    find_series,
    find_series_by_id,
    show_series,
    sort_series_by_issues,
)
from models.users import add_user, find_user_by_id, show_users
from storage import (
    load_collection,
    load_series,
    load_users,
    save_collection,
    save_series,
    save_users,
)
from utils import input_int, input_nonempty_str

SERIES_FILE = "data/series.json"
USERS_FILE = "data/users.json"
COLLECTION_FILE = "data/collection.json"

MENU = """
=== Сервис учёта комиксов ===
1. Показать серии
2. Найти серию по названию
3. Проверить возрастной доступ к серии для текущего пользователя
4. Добавить новую серию
5. Показать пользователей
6. Добавить пользователя
7. Сменить текущего пользователя
8. Показать мою коллекцию
9. Добавить серию в мою коллекцию
10. Обновить прогресс чтения
11. Удалить запись из коллекции
0. Выход
"""


def seed_initial_data() -> tuple:
    """Сформировать исходные данные на основе сценария ПР1.

    Используется, если файлы данных отсутствуют: воссоздаёт пример
    из начального сценария (пользователь Даниил, серия The Sandman,
    статус чтения «читаю»).
    """
    users: List[User] = [User(1, "Даниил", 21, "daniil@example.com")]
    series_list: List[Series] = [
        Series(1, "The Sandman", "DC Comics", "Neil Gaiman", 75, 18)
    ]
    collection: List[CollectionEntry] = [
        CollectionEntry(1, series_list[0], users[0], STATUS_READING, 31)
    ]
    return series_list, users, collection


def create_new_series(series_list: List[Series]) -> None:
    """Добавить новую серию по данным, введённым пользователем."""
    title = input_nonempty_str("Название серии: ")
    publisher = input_nonempty_str("Издатель: ")
    author = input_nonempty_str("Автор: ")
    issues_total = input_int("Всего выпусков в серии: ")
    age_limit = input_int("Возрастное ограничение: ")
    series = add_series(
        series_list, title, publisher, author, issues_total, age_limit
    )
    print(f"Добавлена серия с идентификатором {series.id}.")


def create_new_user(users: List[User]) -> User:
    """Добавить нового пользователя по данным, введённым с клавиатуры."""
    name = input_nonempty_str("Имя пользователя: ")
    age = input_int("Возраст: ")
    email = input_nonempty_str("Адрес электронной почты: ")
    user = add_user(users, name, age, email)
    print(f"Добавлен пользователь с идентификатором {user.id}.")
    return user


def select_current_user(users: List[User], current_user: User) -> User:
    """Выполнить сценарий смены текущего пользователя."""
    show_users(users)
    user_id = input_int("Идентификатор пользователя: ")
    user = find_user_by_id(users, user_id)
    if user is None:
        print("Пользователь с таким идентификатором не найден.")
        return current_user
    print(f"Текущий пользователь: {user}")
    return user


@log_action
def create_new_collection_entry(
    collection: List[CollectionEntry],
    series_list: List[Series],
    user: User,
) -> None:
    """Выполнить пользовательский сценарий добавления серии в коллекцию."""
    series_id = input_int("Идентификатор серии: ")
    series = find_series_by_id(series_list, series_id)
    if series is None:
        print("Серия с таким идентификатором не найдена.")
        return

    already_in_collection = is_series_in_collection(collection, series)
    is_available = not already_in_collection and series.is_suitable_for(user.age)
    print(get_collection_status(is_available))

    entry = add_to_collection(collection, series, user, STATUS_PLANNED)
    if entry is None:
        if not already_in_collection:
            print(
                "Операция отменена: возрастное ограничение "
                f"{series.age_limit}+, ваш возраст — {user.age}."
            )
        return
    print(f"Серия добавлена в коллекцию, идентификатор записи {entry.id}.")


def update_collection_progress(collection: List[CollectionEntry]) -> None:
    """Выполнить пользовательский сценарий обновления прогресса чтения."""
    entry_id = input_int("Идентификатор записи коллекции: ")
    issues_read = input_int("Прочитано выпусков: ")
    if update_issues_read(collection, entry_id, issues_read):
        print("Прогресс обновлён.")
    else:
        print("Запись коллекции с таким идентификатором не найдена.")


@log_action
def remove_collection_entry(collection: List[CollectionEntry]) -> None:
    """Выполнить пользовательский сценарий удаления записи коллекции."""
    entry_id = input_int("Идентификатор записи коллекции: ")
    if remove_from_collection(collection, entry_id):
        print("Запись удалена из коллекции.")
    else:
        print("Запись коллекции с таким идентификатором не найдена.")


def show_my_collection(
    collection: List[CollectionEntry],
    user: User,
) -> None:
    """Вывести записи коллекции, принадлежащие текущему пользователю."""
    show_collection([entry for entry in collection if entry.user.id == user.id])


def main() -> None:
    """Точка запуска приложения: главное меню и работа с объектами."""
    series_list = load_series(SERIES_FILE)
    users = load_users(USERS_FILE)
    collection = load_collection(COLLECTION_FILE, series_list, users)
    if not series_list and not users:
        series_list, users, collection = seed_initial_data()

    current_user: Optional[User] = users[0] if users else None
    if current_user is None:
        current_user = create_new_user(users)
    print(f"Текущий пользователь: {current_user}")

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
            if check_series_age_limit(series_list, series_id, current_user.age):
                print("Серия доступна по возрасту.")
            else:
                print("Серия недоступна по возрасту или не найдена.")
        elif choice == 4:
            create_new_series(series_list)
        elif choice == 5:
            show_users(users)
        elif choice == 6:
            create_new_user(users)
        elif choice == 7:
            current_user = select_current_user(users, current_user)
        elif choice == 8:
            show_my_collection(collection, current_user)
        elif choice == 9:
            create_new_collection_entry(collection, series_list, current_user)
        elif choice == 10:
            update_collection_progress(collection)
        elif choice == 11:
            remove_collection_entry(collection)
        elif choice == 0:
            save_series(SERIES_FILE, series_list)
            save_users(USERS_FILE, users)
            save_collection(COLLECTION_FILE, collection)
            print("Данные сохранены. До встречи!")
            break
        else:
            print("Неизвестный пункт меню.")

    sorted_by_issues = sort_series_by_issues(series_list)
    if sorted_by_issues:
        shortest = sorted_by_issues[0]
        print(f"Самая короткая серия в базе: {shortest.title}.")


if __name__ == "__main__":
    main()
