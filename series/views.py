"""Представления страниц серий комиксов (данные берутся из JSON, ПР5)."""

from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models.collection import is_series_in_collection
from models.series import find_series_by_id
from storage import load_collection, load_series, load_users


def series_list(request):
    """Страница /series/: список серий из data/series.json."""
    items = ""
    for series in load_series(str(settings.DATA_DIR / "series.json")):
        text = (
            f"{escape(series.title)} – {series.issues_total} выпусков, "
            f"{series.age_limit}+"
        )
        items += (
            '<li class="list-group-item">'
            f'<a href="/series/{series.id}/">{text}</a></li>'
        )
    content = f"""
    <h1>Серии</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Сервис учёта комиксов – серии", content))


def series_detail(request, series_id):
    """Страница /series/<id>/: карточка серии и признак наличия в коллекции."""
    series_items = load_series(str(settings.DATA_DIR / "series.json"))
    series = find_series_by_id(series_items, series_id)

    if series is None:
        content = """
        <h1 class="text-danger">Серия не найдена</h1>
        <a href="/series/" class="btn btn-outline-secondary">
            ← к списку серий
        </a>
        """
        return HttpResponse(page("Серия не найдена", content), status=404)

    users = load_users(str(settings.DATA_DIR / "users.json"))
    collection = load_collection(
        str(settings.DATA_DIR / "collection.json"),
        series_items,
        users,
    )
    in_collection = is_series_in_collection(collection, series)
    status = "в коллекции" if in_collection else "не в коллекции"
    badge = "bg-success" if in_collection else "bg-secondary"

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(series.title)}</h5>
            <p class="card-text"><strong>ID:</strong> {series.id}</p>
            <p class="card-text">
                <strong>Издатель:</strong> {escape(series.publisher)}
            </p>
            <p class="card-text">
                <strong>Автор:</strong> {escape(series.author)}
            </p>
            <p class="card-text">
                <strong>Выпусков:</strong> {series.issues_total}
            </p>
            <p class="card-text">
                <strong>Возрастное ограничение:</strong> {series.age_limit}+
            </p>
            <p class="card-text">
                Состояние:
                <span class="badge {badge}">{status}</span>
            </p>
            <a href="/series/" class="btn btn-outline-secondary">
                ← к списку серий
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(series.title, content), status=200)
