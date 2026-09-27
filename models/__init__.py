"""Пакет моделей предметной области сервиса учёта комиксов."""

from .collection import CollectionEntry
from .series import Series
from .users import User

__all__ = ["Series", "User", "CollectionEntry"]
