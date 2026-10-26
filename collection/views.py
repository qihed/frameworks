"""Представления страниц коллекции (данные берутся из JSON)."""

from django.conf import settings
from django.shortcuts import render

from models.collection import find_entry_by_id
from storage import load_collection, load_series, load_users


def _load_entries():
    """Загрузить записи коллекции вместе со связанными объектами."""
    series_items = load_series(str(settings.DATA_DIR / "series.json"))
    users = load_users(str(settings.DATA_DIR / "users.json"))
    return load_collection(
        str(settings.DATA_DIR / "collection.json"),
        series_items,
        users,
    )


def collection_list(request):
    """Страница /collection/: список записей коллекции."""
    context = {
        "entries": _load_entries(),
    }

    return render(
        request,
        "collection/entry_list.html",
        context,
    )


def entry_detail(request, entry_id):
    """Страница /collection/<id>/: запись коллекции со связанными данными."""
    entry = find_entry_by_id(_load_entries(), entry_id)

    context = {
        "entry": entry,
    }

    return render(
        request,
        "collection/entry_detail.html",
        context,
        status=404 if entry is None else 200,
    )
