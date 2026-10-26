from django.urls import path

from . import views

urlpatterns = [
    path("", views.series_list, name="series_list"),
    path("<int:series_id>/", views.series_detail, name="series_detail"),
]
