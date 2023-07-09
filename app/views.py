from django.db import IntegrityError

from .scripts import credentials
from .models import *
from .api import *

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

import requests
import json
import openai


# This function handles the index page
def index(request):
    if not request.user.is_authenticated:
        pass
    else:
        # Redirect to the home page
        return HttpResponseRedirect(reverse("home"))


# Handles the page where the user gets asked basic information and health information
def survey(request):
    if request.method == 'POST':
        pass


# This handles the home page
# This page should show you weight history and stuffs
@login_required
def home(request):
    return HttpResponse("Hello " + request.user.username)


@login_required
# Renders the diary page
def diary(request):
    pass


# Handles the page where you can talk to chatGPT
@login_required
def ask_ai(request):
    daily_entry, created = DailyEntry.objects.get_or_create(user=request.user)
    ask_meal_plan_gpt(request.user)
    return HttpResponse(daily_entry.user_foods)


@login_required
def settings(request):
    pass


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "app/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "app/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "app/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")


# Renders the error page
def error(request):
    pass
