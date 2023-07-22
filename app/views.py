from django.db import IntegrityError

from .scripts import credentials
from .models import *
from .api import *
from .forms import *

from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from datetime import date, datetime
from htmlgenerator import DIV, P, SPAN
from htmlgenerator import render as R

import requests
import json
import openai

AVAILABLE_PROMPTS = {
    "Analyze my history": ai_analyze_history,
    "Recommend me a meal plan": ask_meal_plan_gpt,
    "Recommend me an exercise routine": ask_exercise_plan_gpt,
}


# This function handles the index page
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))
    return HttpResponseRedirect(reverse("login"))


# Handles the page where the user gets asked basic information and health information
def survey(request):
    if request.method == "POST":
        pass


# This handles the home page
# This page should show you weight history and stuffs
@login_required
def home(request):
    return render(request, "layout.html")


@login_required
# Renders the diary page
def diary(request):
    if request.method == "GET":
        daily_entry, _ = DailyEntry.objects.get_or_create(
            user=request.user, date=datetime.now()
        )
        return render(
            request,
            "diary.html",
            {"daily_entry": daily_entry.summarize(), "user_food_form": UserFoodForm()},
        )


@login_required
# Handles food databse queries and add new entries to the database
def food(request):
    if request.method == "GET":
        food_id = request.GET.get("foodId", "")
        search = request.GET.get("search", "")
        # If the user wants to obtain more detailed data about a specific food
        if food_id:
            daily_entry_date = request.GET.get("date", str(date.today()))
            # The first object is the one we want
            food = analyze_food(food_id)[0]
            return HttpResponse(food.user_food_form(request, daily_entry_date))
        # If the user just wants to search for food in the database
        else:
            search_results = autocomplete_search(search)
            response = ""
            for food_name in search_results:
                analyze_food(food_name)
            # Turn each food object into an html form
            for food in Food.objects.filter(label__icontains=search)[0:40]:
                response += food.html_table_format()
            return HttpResponse(response)
    if request.method == "POST":
        form = UserFoodForm(request.POST)
        print(form.errors)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            time_added = form.cleaned_data["time_added"]
            unit = form.cleaned_data["unit"]
            food_id = form.cleaned_data["food_id"]
            daily_entry_date = form.cleaned_data["daily_entry_date"]
            daily_entry, _ = DailyEntry.objects.get_or_create(
                user=request.user, date=daily_entry_date
            )
            # TODO: Make a system that handle different units
            new_user_food = UserFood.objects.create(
                daily_entry=daily_entry,
                time_added=time_added,
                weight=amount,
                food_id=food_id,
            )
            return HttpResponse(new_user_food.html_table_format())


# Handles the page where you can talk to chatGPT
@login_required
def ask_ai(request):
    # If requested by htmx
    if request.htmx:
        if request.method == "GET":
            prompt = request.GET.get("prompt", "")
            if not prompt:
                return HttpResponse("NOT WORKING!")
            elif prompt == "Analyze my history":
                number_of_days = request.GET.get("days", 30)
                response = ai_analyze_history(request.user, number_of_days)
                return HttpResponse(response)
            elif prompt == "Recommend me a meal plan":
                gpt_response = ask_meal_plan_gpt(request.user)
                vals = {"gptResponse": gpt_response}
                response = DIV(
                    P(gpt_response),
                    SPAN(
                        P("Import meal plan?"),
                        DIV(
                            "YES",
                            hx_post="askai",
                            hx_vals=json.dumps(vals),
                            hx_swap="outerHTML",
                            _class="btn btn-outline btn-success",
                        ),
                        DIV("NO", _class="btn btn-outline btn-danger"),
                    ),
                )
                return HttpResponse(R(response, {}))
            elif prompt == "Recommend me an exercise routine":
                response = ask_exercise_plan_gpt(request.user)
                return HttpResponse(response)
            return HttpResponse("Non-existent prompt")
        # If user wants to import
        if request.method == "POST":
            gpt_response = request.POST.get("gptResponse")
            if import_user_meal_plan(request.user, gpt_response):
                return HttpResponse(
                    R(DIV("Import Completed", _class="alert alert-success"), {})
                )
            else:
                return HttpResponse(
                    R(DIV("Import Failed", _class="alert alert-failed"), {})
                )
    else:
        return render(request, "askai.html", {"prompts": AVAILABLE_PROMPTS.keys()})


@login_required
def settings(request):
    pass


def login_view(request):
    if request.user.is_authenticated:
        return request(reverse("home"))
    if request.method == "POST":
        print(request.POST)
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            print("User does exist")
            login(request, user)
            return redirect(reverse("home"))
        else:
            print("Invalid User")
            return render(
                request, "login.html", {"message": "Invalid username and/or password."}
            )
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
            return render(
                request, "register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, "register.html")


# Renders the error page
def error(request):
    pass
