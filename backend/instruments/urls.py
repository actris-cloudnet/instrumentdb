from django.contrib.auth import views as auth_views
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
    path(
        "instrument/<instrument_uuid>/create_pid", views.create_pid, name="create_pid"
    ),
    path("instrument/<instrument_uuid>/pi", views.pi, name="pi"),
    path(
        "login",
        auth_views.LoginView.as_view(template_name="instruments/login.html"),
        name="login",
    ),
    path(
        "logout",
        auth_views.LogoutView.as_view(template_name="instruments/logout.html"),
        name="logout",
    ),
]
