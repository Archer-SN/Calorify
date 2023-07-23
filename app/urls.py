from django.urls import path

from . import views

urlpatterns = [

    path("", views.index, name="index"),

    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("error", views.error, name="error"),


    path("home", views.home, name="home"),
    path("diary", views.diary, name="diary"),
    path("settings", views.settings, name="settings"),

    path("askai", views.ask_ai, name="askai"),
    
    path("food", views.food, name="food"),    
    path("challenge", views.challenge, name="challenge"),

    path("empty", views.empty, name="empty")
]