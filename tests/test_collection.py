"""Тесты класса CollectionEntry и функций коллекции (models/collection.py)."""

from models import Series, User
from models.collection import (
    add_to_collection,
    is_series_in_collection,
    remove_from_collection,
)


def _make_series() -> Series:
    return Series(1, "The Sandman", "DC Comics", "Neil Gaiman", 75, 18)


def _make_user(age: int = 20) -> User:
    return User(1, "Иван Петров", age, "ivan@example.com")


def test_collection_entry_creation():
    series = _make_series()
    user = _make_user()
    entry = add_to_collection([], series, user)
    assert entry is not None
    assert entry.id == 1
    assert entry.series is series
    assert entry.user is user
    assert entry.status == "запланировано"


def test_collection_entry_remove():
    series = _make_series()
    user = _make_user()
    collection = []
    entry = add_to_collection(collection, series, user)
    entry.remove()
    assert entry.is_removed
    assert entry.status == "удалено из коллекции"


def test_add_to_collection_forbidden_by_age():
    series = _make_series()
    user = _make_user(age=15)
    collection = []
    entry = add_to_collection(collection, series, user)
    assert entry is None
    assert len(collection) == 0


def test_duplicate_add_forbidden():
    series = _make_series()
    user = _make_user()
    collection = []
    add_to_collection(collection, series, user)
    entry = add_to_collection(collection, series, user)
    assert entry is None
    assert len(collection) == 1


def test_remove_from_collection_allows_re_adding():
    series = _make_series()
    user = _make_user()
    collection = []
    first_entry = add_to_collection(collection, series, user)

    assert remove_from_collection(collection, first_entry.id)
    assert not is_series_in_collection(collection, series)

    second_entry = add_to_collection(collection, series, user)
    assert second_entry is not None
    assert len(collection) == 2


def test_calculate_progress_and_issues_left():
    series = _make_series()
    user = _make_user()
    collection = []
    entry = add_to_collection(collection, series, user)
    entry.issues_read = 31
    assert entry.calculate_progress() == 31 / 75 * 100
    assert entry.count_issues_left() == 44
    assert len(collection) == 1
