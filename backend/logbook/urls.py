from django.urls import path

from . import views

app_name = "logbook"
urlpatterns = [
    path("instrument/<instrument_uuid>/logbook", views.view, name="view"),
    path("instrument/<instrument_uuid>/logbook/add", views.add, name="add"),
    path(
        "instrument/<instrument_uuid>/logbook/<int:entry_id>", views.edit, name="edit"
    ),
    path(
        "instrument/<instrument_uuid>/logbook/<int:entry_id>/delete",
        views.delete,
        name="delete",
    ),
]
