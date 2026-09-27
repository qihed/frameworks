"""Тесты класса Series и функций работы с сериями (models/series.py)."""

from models import Series
from models.series import (
    add_series,
    check_series_age_limit,
    filter_series_by_age_limit,
    find_series,
    sort_series_by_issues,
)


def test_series_creation():
    series = Series(1, "The Sandman", "DC Comics", "Neil Gaiman", 75, 18)
    assert series.id == 1
    assert series.title == "The Sandman"
    assert series.issues_total == 75
    assert series.age_limit == 18


def test_series_is_suitable_for():
    series = Series(1, "The Sandman", "DC Comics", "Neil Gaiman", 75, 18)
    assert series.is_suitable_for(20)
    assert not series.is_suitable_for(15)


def test_series_validate_age_limit():
    assert Series.validate_age_limit(18)
    assert not Series.validate_age_limit(-1)


def test_add_series():
    series_list = []
    series = add_series(
        series_list, "Berserk", "Hakusensha", "Kentaro Miura", 40, 18
    )
    assert len(series_list) == 1
    assert series.id == 1


def test_find_series():
    series_list = []
    add_series(series_list, "The Sandman", "DC Comics", "Neil Gaiman", 75, 18)
    result = find_series(series_list, "sandman")
    assert len(result) == 1
    assert result[0].title == "The Sandman"


def test_check_series_age_limit():
    series_list = []
    add_series(series_list, "The Sandman", "DC Comics", "Neil Gaiman", 75, 18)
    assert check_series_age_limit(series_list, 1, 20)
    assert not check_series_age_limit(series_list, 1, 15)


def test_filter_series_by_age_limit():
    series_list = []
    add_series(
        series_list, "Naruto", "Shueisha", "Masashi Kishimoto", 700, 12
    )
    add_series(series_list, "Berserk", "Hakusensha", "Kentaro Miura", 40, 18)
    result = filter_series_by_age_limit(series_list, 12)
    assert len(result) == 1
    assert result[0].title == "Naruto"


def test_sort_series_by_issues():
    series_list = []
    add_series(
        series_list, "Naruto", "Shueisha", "Masashi Kishimoto", 700, 12
    )
    add_series(series_list, "Berserk", "Hakusensha", "Kentaro Miura", 40, 18)
    result = sort_series_by_issues(series_list)
    assert result[0].title == "Berserk"
