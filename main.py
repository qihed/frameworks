"""Сервис учёта комиксов.

Начальный сценарий индивидуального сквозного проекта (практическая работа № 1).
Сценарий: читатель добавляет выпуск комикса в свою коллекцию, отмечает состояние
чтения и смотрит, насколько продвинулся по серии.

В программе используются только конструкции, изученные в рамках ПР1: простые типы
данных, операции над ними, преобразование типов, ветвления, функции и импорт
модулей. Работа с коллекциями, циклами и классами выполняется на следующих этапах.
"""

from datetime import date

# Коды состояний выпуска у пользователя.
STATUS_PLANNED = 1
STATUS_READING = 2
STATUS_FINISHED = 3
STATUS_DROPPED = 4


def get_status_name(status_code):
    """Вернуть читаемое название состояния выпуска по его коду."""
    if status_code == STATUS_PLANNED:
        return "запланировано"
    elif status_code == STATUS_READING:
        return "читаю"
    elif status_code == STATUS_FINISHED:
        return "прочитано"
    elif status_code == STATUS_DROPPED:
        return "брошено"
    return "состояние не определено"


def can_add_to_collection(is_in_collection, user_age, age_limit):
    """Проверить, можно ли добавить выпуск в коллекцию пользователя.

    Выпуск добавляется, если его ещё нет в коллекции и возраст пользователя
    не меньше возрастного ограничения издания.
    """
    return not is_in_collection and user_age >= age_limit


def calculate_progress(issues_read, issues_total):
    """Рассчитать прогресс чтения серии в процентах."""
    if issues_total <= 0:
        return 0.0
    if issues_read > issues_total:
        issues_read = issues_total
    return issues_read / issues_total * 100


def count_issues_left(issues_read, issues_total):
    """Посчитать, сколько выпусков серии осталось прочитать."""
    if issues_read >= issues_total:
        return 0
    return issues_total - issues_read


def format_comic_card(comic_title, issue_number, release_year, status_code):
    """Собрать карточку выпуска для вывода пользователю."""
    status_name = get_status_name(status_code)
    return (
        f"{comic_title} (выпуск № {issue_number}, {release_year} г.) "
        f"— {status_name}"
    )


# Сведения о пользователе.
user_name = "Даниил"
user_age = 21
registered_at = date(2026, 9, 1)

# Сведения о серии и выпуске.
series_title = "The Sandman"
series_publisher = "DC Comics"
series_issues_total = 75
comic_title = "The Sandman: Season of Mists"
issue_number = 21
release_year = 1990
age_limit = 18

# Состояние выпуска у пользователя.
is_in_collection = False
status_code = STATUS_READING

# Число прочитанных выпусков приходит строкой, например из ввода пользователя,
# поэтому требуется преобразование типа.
issues_read_raw = "31"
issues_read = int(issues_read_raw)

progress = calculate_progress(issues_read, series_issues_total)
issues_left = count_issues_left(issues_read, series_issues_total)
is_addition_allowed = can_add_to_collection(is_in_collection, user_age, age_limit)

print("СЕРВИС УЧЁТА КОМИКСОВ")
print("=" * 46)
print(f"Пользователь: {user_name}")
print(f"Возраст: {user_age}")
print(f"В сервисе с: {registered_at}")
print()
print(f"Серия: {series_title} ({series_publisher})")
print(f"Выпусков в серии: {series_issues_total}")
print(f"Прочитано выпусков: {issues_read}")
print(f"Прогресс по серии: {round(progress, 1)} %")
print(f"Осталось прочитать: {issues_left}")
print()
print("Карточка выпуска:")
print(format_comic_card(comic_title, issue_number, release_year, status_code))
print()

if is_addition_allowed:
    print("Выпуск можно добавить в коллекцию.")
elif is_in_collection:
    print("Выпуск уже находится в коллекции.")
else:
    print(
        "Выпуск недоступен: возрастное ограничение "
        f"{age_limit}+, возраст пользователя — {user_age}."
    )

if progress >= 100:
    print("Серия прочитана полностью.")
elif progress >= 50:
    print("Серия пройдена больше чем наполовину.")
else:
    print("Серия пройдена меньше чем наполовину.")
