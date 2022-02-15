from django.urls import path

from . import views

urlpatterns = [
    path(
        "instrument/<instrument_uuid>.html",
        views.instrument_html,
        name="instrument_html",
    ),
    path(
        "instrument/<instrument_uuid>.xml",
        views.instrument_xml,
        name="instrument_xml",
    ),
    path(
        "instrument/<instrument_uuid>.json",
        views.instrument_json,
        name="instrument_json",
    ),
]
