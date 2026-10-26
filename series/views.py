"""Представления страниц серий комиксов (данные берутся из JSON)."""

from django.conf import settings
from django.shortcuts import render

from models.collection import is_series_in_collection
from models.series import find_series_by_id
from storage import load_collection, load_series, load_users


def series_list(request):
    """Страница /series/: список серий из data/series.json."""
    series_items = load_series(str(settings.DATA_DIR / "series.json"))

    context = {
        "series_items": series_items,
    }

    return render(
        request,
        "series/series_list.html",
        context,
    )


def series_detail(request, series_id):
    """Страница /series/<id>/: карточка серии и признак наличия в коллекции."""
    series_items = load_series(str(settings.DATA_DIR / "series.json"))
    series = find_series_by_id(series_items, series_id)

    in_collection = False
    if series is not None:
        users = load_users(str(settings.DATA_DIR / "users.json"))
        collection = load_collection(
            str(settings.DATA_DIR / "collection.json"),
            series_items,
            users,
        )
        in_collection = is_series_in_collection(collection, series)

    context = {
        "series": series,
        "in_collection": in_collection,
    }

    return render(
        request,
        "series/series_detail.html",
        context,
        status=404 if series is None else 200,
    )
