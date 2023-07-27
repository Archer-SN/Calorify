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
from htmlgenerator import DIV, P, SPAN, FORM, BUTTON
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
    # Initialize the food database for a very new database
    if not Nutrient.objects.filter().exists():
        food_database_init()
    user = request.user
    total_nutrients = Counter()
    daily_entries = DailyEntry.objects.filter(user=user)
    daily_entries_count = daily_entries.count()
    for daily_entry in daily_entries:
        total_nutrients += Counter(daily_entry.total_nutrients())
    average_nutrients = total_nutrients
    for nutrient in total_nutrients.keys():
        average_nutrients[nutrient] = round(
            average_nutrients[nutrient] / daily_entries_count, 1
        )

    return render(
        request,
        "home.html",
        {
            "user_info": user.info(),
            "AVG": {
                "energy": average_nutrients[ENERGY],
                "protein": average_nutrients[PROTEIN],
                "carbs": average_nutrients[CARBS],
                "fats": average_nutrients[FATS],
            },
        },
    )


@login_required
# Renders the diary page
def diary(request):
    if request.method == "GET":
        user = request.user
        daily_entry, _ = DailyEntry.objects.get_or_create(
            user=user, date=datetime.now()
        )
        challenges = Challenge.objects.filter(user=user)
        challenges_info = []
        for challenge in challenges:
            if not challenge.is_completed:
                challenges_info.append(challenge.info())
        return render(
            request,
            "diary.html",
            {
                "daily_entry": daily_entry.summarize(),
                "user_food_form": UserFoodForm(),
                "challenges": challenges_info,
            },
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
            for food in Food.objects.filter(label__icontains=search)[0:20]:
                response += food.html_table_format()
            return HttpResponse(response)


@login_required
def user_food(request):
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
    elif request.method == "DELETE":
        print("hello")
        return HttpResponse()


@login_required
def exercise(request):
    if request.method == "GET":
        user = request.user
        return ask_exercise_plan_gpt(user)


@login_required
def challenge(request):
    if request.htmx:
        # User checks out the challenge
        if request.method == "POST":
            challenge_id = request.POST.get("challengeId", "")
            user = request.user
            if not challenge_id:
                return HttpResponse(
                    "Challenge does not exist. Challenge ID: " + challenge_id
                )
            print(1)
            user_challenge = Challenge.objects.get(id=challenge_id, user=user)
            if user_challenge.is_completed:
                return HttpResponse("ALready Done")
            user_challenge.complete_challenge()
            # TODO: Make this more elegant
            user_challenge.is_completed = True
            user_challenge.save()
            return HttpResponse()
    else:
        pass


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
                gpt_response = ai_analyze_history(request.user, number_of_days)
                response = DIV(
                    H1("History Analysis", _class="text-lg font-bold"), P(gpt_response)
                )
                return HttpResponse(R(response, {}))
            elif prompt == "Recommend me a meal plan":
                gpt_response = ask_meal_plan_gpt(request.user)
                vals = {"gptResponse": gpt_response}
                response = DIV(
                    gpt_response,
                    SPAN(
                        P("Import meal plan?"),
                        DIV(
                            "YES",
                            hx_post="askai",
                            hx_vals=json.dumps(vals),
                            hx_swap="outerHTML",
                            hx_target="closest span",
                            hx_indicator=".htmx-indicator",
                            _class="btn btn-outline btn-success",
                        ),
                        DIV(
                            "NO",
                            _class="btn btn-outline btn-danger",
                            hx_get="empty",
                            hx_swap="delete",
                            hx_indicator=".htmx-indicator",
                            hx_target="closest span",
                        ),
                    ),
                    _class="border-solid border-2 p-3",
                )
                return HttpResponse(R(response, {}))
            elif prompt == "Recommend me an exercise routine":
                gpt_response = ask_exercise_plan_gpt(request.user)
                response = DIV(P(gpt_response))
                return HttpResponse(R(response, {}))
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
    if request.htmx:
        # User submitted account information
        if request.method == "POST":
            if not request.user.is_authenticated:
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
                # Ask the user about their information
                form = UserForm().as_div()
                response = FORM(
                    form,
                    BUTTON(
                        "Submit", type="submit", _class="btn btn-outline btn-primary"
                    ),
                    hx_get="register",
                    hx_swap="innerHTML",
                    _class="form-control flex flex-col space-y-4 md:space-y-6",
                )
                return HttpResponse(R(response, {}))
        # User submitted health data
        # TODO: GET FOR NOW, THOUGH WE WANT POST
        elif request.method == "GET":
            form = UserForm(request.GET)
            user = request.user
            print(form.errors)
            if user.is_authenticated and form.is_valid():
                date_born = form.cleaned_data["date_born"]
                sex = form.cleaned_data["sex"]
                height = form.cleaned_data["height"]
                weight = form.cleaned_data["weight"]
                body_fat = form.cleaned_data["body_fat"]
                activity_level = form.cleaned_data["activity_level"]
                meal_frequency = form.cleaned_data["meal_frequency"]
                recommendation_frequency = form.cleaned_data["recommendation_frequency"]
                weight_goal = form.cleaned_data["weight_goal"]
                weight_goal_rate = form.cleaned_data["weight_goal_rate"]
                User.objects.filter(id=user.id).update(
                    date_born=date_born,
                    sex=sex,
                    height=height,
                    weight=weight,
                    body_fat=body_fat,
                    activity_level=activity_level,
                    meal_frequency=meal_frequency,
                    recommendation_frequency=recommendation_frequency,
                )
                UserTargets.objects.filter(user=user).update(
                    weight_goal=weight_goal, weight_goal_rate=weight_goal_rate
                )
                response = HttpResponse()
                response["HX-Redirect"] = reverse("home")
                return response
        # Return the form if the input is wrong
        form = UserForm(request.GET).as_div()
        response = FORM(
            form,
            BUTTON("Submit", type="submit", _class="btn btn-outline btn-primary"),
            hx_get="register",
            hx_swap="innerHTML",
            _class="form-control flex flex-col space-y-4 md:space-y-6",
        )
        return HttpResponse(R(response, {}))
    # If not a request from HTMX, but normal forms
    else:
        if request.user.is_authenticated:
            return redirect(reverse("home"))
        return render(request, "register.html")


# Renders the error page
def error(request):
    pass


# This is used for making empty HTMX requests
# Use case: Deleting elements
def empty(request):
    return HttpResponse()
