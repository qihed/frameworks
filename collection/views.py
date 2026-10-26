"""Представления страниц коллекции (данные берутся из JSON, ПР5)."""

from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
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
    items = ""
    for entry in _load_entries():
        badge = "bg-secondary" if entry.is_removed else "bg-success"
        items += f"""
        <li class="list-group-item d-flex justify-content-between">
            <a href="/collection/{entry.id}/">
                {escape(entry.series.title)} – {escape(entry.user.name)}
            </a>
            <span class="badge {badge}">{escape(entry.status)}</span>
        </li>
        """
    content = f"""
    <h1>Коллекция</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Сервис учёта комиксов – коллекция", content))


def entry_detail(request, entry_id):
    """Страница /collection/<id>/: запись коллекции со связанными данными."""
    entry = find_entry_by_id(_load_entries(), entry_id)

    if entry is None:
        content = """
        <h1 class="text-danger">Запись коллекции не найдена</h1>
        <a href="/collection/" class="btn btn-outline-secondary">
            ← к коллекции
        </a>
        """
        return HttpResponse(
            page("Запись коллекции не найдена", content),
            status=404,
        )

    badge = "bg-secondary" if entry.is_removed else "bg-success"
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Запись коллекции №{entry.id}</h5>
            <p class="card-text">
                <strong>Серия:</strong> {escape(entry.series.title)}
            </p>
            <p class="card-text">
                <strong>Пользователь:</strong> {escape(entry.user.name)}
            </p>
            <p class="card-text">
                <strong>Прогресс:</strong> {entry.issues_read} из
                {entry.series.issues_total}
                ({entry.calculate_progress():.1f} %)
            </p>
            <p class="card-text">
                <strong>Осталось прочитать:</strong>
                {entry.count_issues_left()}
            </p>
            <p class="card-text">
                <strong>Статус:</strong>
                <span class="badge {badge}">{escape(entry.status)}</span>
            </p>
            <a href="/collection/" class="btn btn-outline-secondary">
                ← к коллекции
            </a>
        </div>
    </div>
    """
    return HttpResponse(
        page(f"Запись коллекции №{entry.id}", content),
        status=200,
    )
