"""Декоратор для журналирования пользовательских сценариев.

Демонстрирует материал темы «Расширенные возможности Python. Декораторы»:
функцию-обёртку, работу с *args/**kwargs произвольной вызываемой функции
и сохранение её имени и документации через functools.wraps.
"""

import functools
from typing import Callable


def log_action(func: Callable) -> Callable:
    """Вывести сообщение о вызове сценария перед его выполнением."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[журнал] выполняется действие: {func.__name__}")
        return func(*args, **kwargs)

    return wrapper
