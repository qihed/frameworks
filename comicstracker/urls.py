"""Корневая маршрутизация проекта: адреса распределяются по приложениям."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("series/", include("series.urls")),
    path("collection/", include("collection.urls")),
]

handler404 = "homepage.views.page_not_found"
