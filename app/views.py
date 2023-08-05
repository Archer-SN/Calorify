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

DATE_FORMAT = "%Y-%m-%d"


# This function handles the index page
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))
    return render(request, "hero.html")


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
        average_nutrients = user.get_average_nutrients()

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
                "streaks": user.get_streaks(),
                "energy_history": user.get_energy_history(),
            },
        )


@login_required
# Handles the diary page
def diary(request):
    if request.method == "GET":
        user = request.user
        challenges_info = []
        # Renders part of the page (Though almost the whole page)
        if request.htmx:
            # Given a new date, renders the body of the page
            chosen_date = request.GET.get("date", datetime.now().strftime(DATE_FORMAT))
            daily_entry, _ = DailyEntry.objects.get_or_create(
                user=user, date=chosen_date
            )
            summary = daily_entry.summarize()
            challenges = Challenge.objects.filter(daily_entry=daily_entry)
            for challenge in challenges:
                if not challenge.is_completed:
                    challenges_info.append(challenge.info())
            context = {**summary, "challenges": challenges_info}
            response = render_block_to_string("diary.html", "body", context)
            return HttpResponse(response)
        # Renders the whole page if not an htmx request
        else:
            daily_entry, _ = DailyEntry.objects.get_or_create(
                user=user, date=datetime.now().strftime(DATE_FORMAT)
            )
            challenges = Challenge.objects.filter(daily_entry=daily_entry)
            for challenge in challenges:
                if not challenge.is_completed:
                    challenges_info.append(challenge.info())
            summary = daily_entry.summarize()
            return render(
                request,
                "diary.html",
                {
                    **summary,
                    "challenges": challenges_info,
                },
            )


@login_required
def store(request):
    if request.htmx:
        # If the user bought something
        if request.method == "POST":
            pass
    return render(request, "store.html")


# Handles obtaining nutrients information from daily entries.
@login_required
def nutrients(request):
    if request.htmx:
        # Given daily entry, returns total nutrients data
        if request.method == "GET":
            user = request.user
            daily_entry_date = request.GET.get("daily_entry_date", datetime.today())
            daily_entry, _ = DailyEntry.objects.get_or_create(
                user=user, date=daily_entry_date
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
            search = request.GET.get("search_food", "")
            if search:
                food_objs = analyze_food(search)
                for food_obj in food_objs:
                    if food_obj not in food_obj_list:
                        food_obj_list.append(food_obj)
            else:
                for food in Food.objects.filter(label__icontains=search)[0:20]:
                    food_obj_list.append(food)
            context = {
                "type": "food",
                "food_data_list": [food_obj.get_data() for food_obj in food_obj_list],
            }
            print(context)
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
                daily_entry_date = request.POST.get(
                    "daily_entry_date", datetime.today()
                )
                daily_entry, _ = DailyEntry.objects.get_or_create(
                    user=request.user, date=daily_entry_date
                )
                # TODO: Make a system that handle different units
                new_user_food = UserFood.objects.create(
                    food_id=food_id,
                    daily_entry=daily_entry,
                    time_added=time_added,
                    weight=amount,
                )
                context = {
                    "food_intake": [new_user_food.get_data()],
                }
                response = render_block_to_string("diary.html", "food_entries", context)
                return HttpResponse(response)
            return HttpResponse()
        elif request.method == "GET":
            food_id = request.GET.get("foodId", "")
            # If the user wants to obtain more detailed data about a specific food
            if food_id:
                daily_entry_date = request.GET.get(
                    "daily_entry_date", str(date.today())
                )
                # The first object is the one we want
                food = analyze_food(food_id, is_importing=True)[0]
                user_food_form = UserFoodForm(
                    initial={
                        "food_id": food_id,
                        "daily_entry_date": daily_entry_date,
                    }
                )
                context = {
                    "type": "food",
                    "food": food.get_macronutrients(),
                    "user_food_form": user_food_form,
                }
                response = render_block_to_string("diary.html", "food_summary", context)
                return HttpResponse(response)


# Handles everything related to Exercise model
@login_required
def exercise(request):
    if request.htmx:
        if request.method == "GET":
            search = request.GET.get("search", "")
            context = {}
            if search:
                params = {"name": search}
                exercise_list = get_exercises(params)
                context = {"exercise_list": exercise_list}
            else:
                # TODO: Only handles StrengthExercise instances for now...
                context = {"exercise_list": StrengthExercise.objects.all()[0:20]}
            response = render_block_to_string(
                "diary.html", "exercise_search_result", context=context, request=request
            )
            return HttpResponse(response)


# Handles the creation, deletion and change of UserExercise object
# TODO: Handle Cardio
@login_required
def user_exercise(request):
    if request.htmx:
        # Creates new UserExercise instance
        if request.method == "POST":
            user_exercise_id = request.POST.get("user_exercise_id")
            form = UserStengthExerciseForm(request.POST)
            # Given a user_exercise_id, delete a UserExercise instance from the databse
            if user_exercise_id:
                UserStrengthExercise.objects.filter(id=user_exercise_id).delete()
                return HttpResponse()
            # The user wants to create a new UserExercise instance
            elif form.is_valid():
                time_added = form.cleaned_data["time_added"]
                sets = form.cleaned_data["sets"]
                reps = form.cleaned_data["reps"]
                weights = form.cleaned_data["weights"]
                exercise_id = form.cleaned_data["exercise_id"]
                daily_entry_date = request.POST.get(
                    "daily_entry_date", datetime.today()
                )
                daily_entry, _ = DailyEntry.objects.get_or_create(
                    user=request.user, date=daily_entry_date
                )
                new_user_exercise = UserStrengthExercise.objects.create(
                    exercise_id=exercise_id,
                    daily_entry=daily_entry,
                    time_added=time_added,
                    sets=sets,
                    reps=reps,
                    weights=weights,
                    user=request.user,
                )
                context = {"user_exercises": [new_user_exercise.get_data()]}
                response = render_block_to_string(
                    "diary.html", "exercise_entries", context
                )
                return HttpResponse(response)
            return HttpResponse()
        elif request.method == "GET":
            exercise_id = request.GET.get("exerciseId", None)
            # If the user wants to obtain more detailed data about a specific exercise
            if exercise_id:
                daily_entry_date = request.GET.get(
                    "daily_entry_date", str(date.today())
                )
                # What to be passed into the api
                params = {"id": exercise_id}
                # The first exercise data is the one we want
                exercise_data = get_exercise_data(params)[0]
                user_exercise_form = UserStengthExerciseForm(
                    initial={
                        "exercise_id": exercise_id,
                        "daily_entry_date": daily_entry_date,
                    },
                )
                context = {
                    "type": "exercise",
                    "exercise_data": exercise_data,
                    "user_exercise_form": user_exercise_form,
                }
                response = render_block_to_string(
                    "diary.html", "exercise_summary", context
                )
                return HttpResponse(response)


@login_required
def challenge(request):
    if request.htmx:
        # User checks out the challenge
        if request.method == "POST":
            challenge_id = request.POST.get("challengeId", "")
            daily_entry_date = request.POST.get("daily_entry_date")
            daily_entry, _ = DailyEntry.objects.get_or_create(
                user=request.user, date=daily_entry_date
            )
            user = request.user
            if not challenge_id:
                return HttpResponse(
                    "Challenge does not exist. Challenge ID: " + challenge_id
                )
            user_challenge = Challenge.objects.get(
                id=challenge_id, daily_entry=daily_entry
            )
            if user_challenge.is_completed:
                return HttpResponse("Already Done")
            user_challenge.complete_challenge(user)
            context = {"user": user}
            response = render_block_to_string("diary.html", "currency", context)
            return HttpResponse(response)
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
                number_of_days = int(request.GET.get("numberOfDays", 30))
                gpt_response = ai_analyze_history(request.user, number_of_days)
                context = {"type": "analysis", "paragraph": gpt_response}
                response = render_block_to_string("askai.html", "gpt_response", context)
                return HttpResponse(response)
            # The user asks to recommend a meal plan
            elif prompt == "Recommend me a meal plan":
                number_of_days = int(request.GET.get("numberOfDays", 30))
                # If the api call is successful, a context should be returned
                context = ask_meal_plan_gpt(request.user)
                response = render_block_to_string("askai.html", "gpt_response", context)
                return HttpResponse(response)
            # The user asks to recommend an exercise routine
            elif prompt == "Recommend me an exercise routine":
                time_available = request.GET.get("timeAvailable", 60)
                exercise_type = request.GET.get("exerciseType")
                # The context should be generated if the AI call is successful
                context = ask_exercise_plan_gpt(
                    request.user,
                    time_available=time_available,
                    exercise_type=exercise_type,
                )
                response = render_block_to_string("askai.html", "gpt_response", context)
                return HttpResponse(response)
            return HttpResponse("Non-existent prompt")
        # If user wants to import
        elif request.method == "POST":
            import_type = request.POST.get("importType")
            if import_type == "food":
                food_dict_list_json = request.POST.get("foodDictList")
                food_dict_list = json.loads(food_dict_list_json)
                # Import successful
                if import_user_meal_plan(request.user, food_dict_list):
                    return HttpResponse()
                # Import failed
                else:
                    return HttpResponse()
            elif import_type == "exercise":
                exercise_schedule = json.loads(request.POST.get("exerciseSchedule"))
                # Import successful
                if import_exercise_plan(exercise_schedule):
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
