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
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from datetime import date, datetime
from render_block import render_block_to_string

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
    if request.htmx:
        pass
    else:
        # Initialize the food database for a very new database
        if not Nutrient.objects.filter().exists():
            food_database_init()
        user = request.user
        # Put this in models.py
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
# Handles the diary page
def diary(request):
    if request.htmx:
        # Given daily entry, returns total nutrients data
        if request.method == "GET":
            daily_entry, _ = DailyEntry.objects.get_or_create(
                user=user, date=datetime.now()
            )
            context = {"nutrient_categories": daily_entry.summarize_nutrients}
            response = render_block_to_string(
                "diary.html", "nutrients_summary", context
            )
            return
    else:
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
            summary = daily_entry.summarize()
            return render(
                request,
                "diary.html",
                {
                    "food_intake": summary["food_intake"],
                    "exercises": summary["exercises"],
                    "nutrient_categories": summary["nutrient_categories"],
                    "challenges": challenges_info,
                },
            )


# Handles obtaining nutrients information from daily entries.
@login_required
def nutrients(request):
    if request.htmx:
        # Given daily entry, returns total nutrients data
        if request.method == "GET":
            user = request.user
            daily_entry, _ = DailyEntry.objects.get_or_create(
                user=user, date=datetime.now()
            )
            context = {"nutrient_categories": daily_entry.summarize_nutrients()}
            response = render_block_to_string(
                "diary.html", "nutrients_summary", context
            )
            return HttpResponse(response)


@login_required
# Handles food databse queries and add new entries to the database
def food(request):
    if request.htmx:
        if request.method == "GET":
            food_obj_list = []
            search = request.GET.get("search", "")
            if search:
                # search_results = autocomplete_search(search)
                # for food_name in search_results:
                #     # is_importing is True so that we analyze only one food (For performance purpose)
                food_objs = analyze_food(search)
                print(food_objs)
                for food_obj in food_objs:
                    if food_obj not in food_obj_list:
                        food_obj_list.append(food_obj)
            else:
                for food in Food.objects.filter(label__icontains=search)[0:20]:
                    food_obj_list.append(food)
            context = {
                "food_data_list": [food_obj.get_data() for food_obj in food_obj_list]
            }
            response = render_block_to_string(
                "diary.html", "food_search_result", context
            )
            return HttpResponse(response)


# Handles everything related to UserFood object
@login_required
def user_food(request):
    if request.htmx:
        # Creates new UserFood instance
        if request.method == "POST":
            user_food_id = request.POST.get("user_food_id")
            form = UserFoodForm(request.POST)
            # Given a user_food_id, delete a UserFood instance from the databse
            if user_food_id:
                UserFood.objects.filter(id=user_food_id).delete()
                return HttpResponse()
            # The user wants to create a new UserFood instance
            elif form.is_valid():
                amount = form.cleaned_data["amount"]
                time_added = form.cleaned_data["time_added"]
                unit = form.cleaned_data["unit"]
                food_id = form.cleaned_data["food_id"]
                daily_entry_date = form.cleaned_data["daily_entry_date"]
                daily_entry, _ = DailyEntry.objects.get_or_create(user=request.user)
                # TODO: Make a system that handle different units
                new_user_food = UserFood.objects.create(
                    food_id=food_id,
                    daily_entry=daily_entry,
                    time_added=time_added,
                    weight=amount,
                )
                context = {
                    "food_intake": [new_user_food.data()],
                    "nutrient_categories": daily_entry.summarize_nutrients(),
                }
                response = render_block_to_string("diary.html", "food_entries", context)
                return HttpResponse(response)
            return HttpResponse()
        elif request.method == "GET":
            food_id = request.GET.get("foodId", "")
            # If the user wants to obtain more detailed data about a specific food
            if food_id:
                daily_entry_date = request.GET.get("date", str(date.today()))
                # The first object is the one we want
                food = analyze_food(food_id)[0]
                user_food_form = UserFoodForm(
                    initial={
                        "food_id": food_id,
                        "daily_entry_date": daily_entry_date,
                    }
                )
                context = {
                    "food": food.get_macronutrients(),
                    "user_food_form": user_food_form,
                }
                response = render_block_to_string("diary.html", "food_summary", context)
                return HttpResponse(response)


# Handles everything related to Exercise model
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
            # The user asks to analyze their history
            elif prompt == "Analyze my history":
                number_of_days = request.GET.get("days", 30)
                gpt_response = ai_analyze_history(request.user, number_of_days)
                context = {"type": "analysis", "paragraph": gpt_response}
                response = render_block_to_string("askai.html", "gpt_response", context)
                return HttpResponse(response)
            # The user asks to recommend a meal plan
            elif prompt == "Recommend me a meal plan":
                # If the api call is successful, a context should be returned
                context = ask_meal_plan_gpt(request.user)
                response = render_block_to_string("askai.html", "gpt_response", context)
                return HttpResponse(response)
            # The user asks to recommend an exercise routine
            elif prompt == "Recommend me an exercise routine":
                gpt_response = ask_exercise_plan_gpt(request.user)
                context = {"type": "exercise", "paragraph": gpt_response}
                response = render_block_to_string("askai.html", "gpt_response", context)
                return HttpResponse(response)
            return HttpResponse("Non-existent prompt")
        # If user wants to import
        elif request.method == "POST":
            print(request.POST)
            food_dict_list_json = request.POST.get("foodDictList")
            food_dict_list = json.loads(food_dict_list_json)
            # Import successful
            if import_user_meal_plan(request.user, food_dict_list):
                return HttpResponse()
            # Import failed
            else:
                return HttpResponse()
        # If the user wants remove something that the AI recommends
        elif request.method == "DELETE":
            pass
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
    return redirect(reverse("login"))


@csrf_protect
def register_view(request):
    if request.htmx:
        # User submitted account information
        if request.method == "POST":
            if not request.user.is_authenticated:
                form = AccountForm(request.POST)
                if form.is_valid():
                    username = form.cleaned_data["username"]
                    email = form.cleaned_data["email"]

                    # Ensure password matches confirmation
                    password = form.cleaned_data["password"]
                    confirmation = form.cleaned_data["password_confirmation"]
                    if password != confirmation:
                        return render(
                            request,
                            "register.html",
                            {"message": "Passwords must match."},
                        )

                    # Attempt to create new user
                    try:
                        user = User.objects.create_user(username, email, password)
                        user.save()
                    except IntegrityError:
                        return render(
                            request,
                            "register.html",
                            {"message": "Username already taken."},
                        )
                    login(request, user)
                    # Ask the user about their information
                    form = HealthInfoForm()
                    context = {"form": form, "form_type": "health"}
                    response = render_block_to_string(
                        "register.html", "form", RequestContext(request, context)
                    )
                    return HttpResponse(response)
        # User submitted health data
        # TODO: We want to use PATCH, but because of csrftoken error thing, we can't do it.
        elif request.method == "GET":
            form = HealthInfoForm(request.GET)
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
        form = HealthInfoForm(request.GET)
        context = {"form": form, "form_type": "account"}
        response = render_block_to_string(
            "register.html", "form", RequestContext(request, context)
        )
        return HttpResponse(response)
    # If not a request from HTMX, but normal forms
    else:
        if request.user.is_authenticated:
            return redirect(reverse("home"))
        return render(
            request, "register.html", {"form": AccountForm(), "form_type": "account"}
        )


# Renders the error page
def error(request):
    pass


# This is used for making empty HTMX requests
# Use case: Deleting elements
def empty(request):
    return HttpResponse()
