from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "instrument/<instrument_uuid>.<output_format>",
        views.instrument,
        name="instrument",
    ),
    path("instrument/<instrument_uuid>", views.instrument, name="instrument"),
    path("instrument/<instrument_uuid>/pi", views.pi, name="pi"),
]
