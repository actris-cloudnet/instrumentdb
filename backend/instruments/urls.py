from django.urls import path

from . import views

urlpatterns = [
    path(
        "instrument/<int:instrument_id>.html",
        views.instrument_html,
        name="instrument_html",
    ),
    path(
        "instrument/<int:instrument_id>.xml",
        views.instrument_xml,
        name="instrument_xml",
    ),
]
