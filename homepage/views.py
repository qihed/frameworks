"""Представления главной страницы и обработчик ошибки 404."""

from django.shortcuts import render


def index(request):
    """Главная страница: описание сервиса и ссылки на разделы."""
    return render(
        request,
        "homepage/index.html",
    )


def page_not_found(request, exception):
    """Собственная страница ошибки 404 для любого неизвестного адреса."""
    return render(
        request,
        "homepage/404.html",
        status=404,
    )
