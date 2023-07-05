from django.urls import path

from . import views

urlpatterns = [

    path("", views.index, name="index"),

    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("error", views.error, name="error"),

    path("diary", views.diary, name="diary"),
    path("settings", views.settings, name="settings")
]