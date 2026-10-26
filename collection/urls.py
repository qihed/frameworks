from django.urls import path

from . import views

urlpatterns = [
    path("", views.collection_list, name="collection_list"),
    path("<int:entry_id>/", views.entry_detail, name="entry_detail"),
]
