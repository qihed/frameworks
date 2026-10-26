from django.urls import path

from . import views

app_name = "series"

urlpatterns = [
    path("", views.series_list, name="list"),
    path("available/", views.available_series, name="available"),
    path("<int:series_id>/", views.series_detail, name="detail"),
]
