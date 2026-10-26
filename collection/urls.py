from django.urls import path

from . import views

app_name = "collection"

urlpatterns = [
    path("", views.collection_list, name="list"),
    path("<int:entry_id>/", views.entry_detail, name="detail"),
]
