"""Вспомогательные функции безопасного ввода данных."""

from datetime import date, datetime


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число.

    При некорректном вводе запрос повторяется, пока пользователь
    не введёт корректное значение.
    """
    while True:
        raw_value = input(prompt)
        try:
            return int(raw_value)
        except ValueError:
            print("Некорректный ввод: ожидалось целое число.")


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату в формате ГГГГ-ММ-ДД."""
    while True:
        raw_value = input(prompt)
        try:
            return datetime.strptime(raw_value, "%Y-%m-%d").date()
        except ValueError:
            print("Некорректный формат даты, пример: 2026-09-15.")


def input_nonempty_str(prompt: str) -> str:
    """Запросить у пользователя непустую строку."""
    while True:
        raw_value = input(prompt).strip()
        if raw_value:
            return raw_value
        print("Значение не может быть пустым.")
