"""Тесты функций работы с коллекцией пользователя (collection.py)."""

from collection import (
    add_to_collection,
    calculate_progress,
    count_issues_left,
    is_series_in_collection,
    remove_from_collection,
)
from series import add_series


def _make_series_list():
    series_list = []
    add_series(series_list, "The Sandman", "DC Comics", "Neil Gaiman", 75, 18)
    return series_list


def test_add_to_collection():
    series_list = _make_series_list()
    collection = []
    entry = add_to_collection(collection, series_list, 1, 20)
    assert entry is not None
    assert len(collection) == 1
    assert is_series_in_collection(collection, 1)


def test_add_to_collection_forbidden_by_age():
    series_list = _make_series_list()
    collection = []
    entry = add_to_collection(collection, series_list, 1, 15)
    assert entry is None
    assert len(collection) == 0


def test_duplicate_add_forbidden():
    series_list = _make_series_list()
    collection = []
    add_to_collection(collection, series_list, 1, 20)
    entry = add_to_collection(collection, series_list, 1, 20)
    assert entry is None
    assert len(collection) == 1


def test_remove_from_collection():
    series_list = _make_series_list()
    collection = []
    entry = add_to_collection(collection, series_list, 1, 20)
    assert remove_from_collection(collection, entry["id"])
    assert not is_series_in_collection(collection, 1)


def test_calculate_progress_and_issues_left():
    assert calculate_progress(31, 75) == 31 / 75 * 100
    assert count_issues_left(31, 75) == 44
    assert count_issues_left(80, 75) == 0
