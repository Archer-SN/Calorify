"""
This file will handle the logic of communicating with API such as EDAMAM, ChatGPT, etc.
"""

from datetime import datetime, timedelta

import openai
import json
import requests

import os
import django
from tenacity import retry, wait_random_exponential, stop_after_attempt
from htmlgenerator import *

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calorify.settings")
django.setup()

from .scripts.credentials import *
from .models import *

openai.api_key = OPEN_AI_KEY

GPT_MODEL = "gpt-3.5-turbo"
# Similar to the above model but can accept more text input
GPT_MODEL_16K = "gpt-3.5-turbo-16k"
GPT_MODEL_4 = "gpt-4"

# Id and Keys for the food database api
EDAMAM_FOOD_DB_ID = "35db61c2"
EDAMAM_FOOD_DB_KEY = EDAMAM_FOOD_DB_KEY

# AP stands for Access Point
# The parser access point handles text search for foods as well as filters for the foods like presence specific nutrient content or exclusion of allergens.
PARSER_AP = "https://api.edamam.com/api/food-database/v2/parser?app_id={app_id}&app_key={app_key}".format(
    app_id=EDAMAM_FOOD_DB_ID, app_key=EDAMAM_FOOD_DB_KEY
)

# In the response to your parser request you receive the a food ID for each database match.
# Using the food ID and the measure URI, which parser provides, you can make a request to the nutrients access point.
# The nutrients access points returns nutrition with diet and health labels for a given quantity of the food.
NUTRIENTS_AP = "https://api.edamam.com/api/food-database/v2/nutrients?app_id={app_id}&app_key={app_key}".format(
    app_id=EDAMAM_FOOD_DB_ID, app_key=EDAMAM_FOOD_DB_KEY
)

# Given a string of text, returns all possible food
AUTOCOMPLETE_AP = (
    "https://api.edamam.com/auto-complete?app_id={app_id}&app_key={app_key}".format(
        app_id=EDAMAM_FOOD_DB_ID, app_key=EDAMAM_FOOD_DB_KEY
    )
)

# Id and keys for the recipe database api
EDAMAM_RECIPE_DB_ID = "c03ec76f"
EDAMAM_RECIPE_DB_KEY = EDAMAM_RECIPE_DB_KEY

# Id and keys for the nutrients analysis api
EDAMAM_NUTRIENTS_ANALYSIS_ID = "8f60cfad"
EDAMAM_NUTRIENTS_ANALYSIS_KEY = EDAMAM_NUTRIENTS_ANALYSIS_KEY

EXERCISE_DB_EP = "https://musclewiki.p.rapidapi.com/exercises"
EXERCISE_DB_HEADERS = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "musclewiki.p.rapidapi.com",
}

STANDARD_MEASURE_UNIT = "g"
STANDARD_MEASURE_URI = "http://www.edamam.com/ontologies/edamam.owl#Measure_gram"
STANDARD_MEASURE_QUANTITY = 100

DEFAULT_SYSTEM_MESSAGE = {
    "role": "system",
    "content": "Assistant is an intelligent chatbot designed to help users answer health, fitness, and cooking related questions. Given each user's data, your advice should be customly made for them. Be concise with your advice. Make sure the food that you give exists in the EDAMAM database.",
}

# I'm not sure whether this should be put in views.py

# TODO: Optimize AI and Models query


# This is just to create all the Nutrient models so that we don't have to create it later on
def food_database_init():
    parser_response = requests.get(PARSER_AP, params={"ingr": "banana"}).json()
    data_list = parser_response["parsed"]
    food_data = data_list[0]["food"]
    ingredients = {
        "ingredients": [
            {
                "quantity": STANDARD_MEASURE_QUANTITY,
                "measureURI": STANDARD_MEASURE_URI,
                "foodId": food_data["foodId"],
            }
        ]
    }
    nutrition_request = requests.post(NUTRIENTS_AP, json=ingredients).json()
    for ntr_code, nutrient_data in nutrition_request["totalNutrients"].items():
        nutrient, nutrient_created = Nutrient.objects.get_or_create(
            id=ntr_code,
            label=nutrient_data["label"],
            unit_name=nutrient_data["unit"],
        )
        print(nutrient)


# Add the given food to the database if it does not yet exist
# We'll call the database with the food weight of 100 grams (A standard weight for storing in the database)
# Return a Food object that is created
def analyze_food(food_name, is_importing=False) -> list:
    parser_params = {"ingr": food_name}
    # Calls the database api to obtain list of foods
    parser_request = requests.get(PARSER_AP, params=parser_params)
    parser_response = parser_request.json()
    if parser_request.status_code == 200:
        food_objs = []
        data_list = None
        # Parsed returns one food
        # Hints returns many
        if "parsed" in parser_response and parser_response["parsed"] and is_importing:
            data_list = parser_response["parsed"]
        else:
            data_list = parser_response["hints"]
        if is_importing:
            data_list = data_list[0:1]
        # Loop through all the data that is returned from the API call
        for data in data_list:
            food_data = data["food"]
            category, category_created = FoodCategory.objects.get_or_create(
                name=food_data["category"]
            )
            # Create the food object if it does not yet exist
            food_obj, food_obj_created = Food.objects.get_or_create(
                id=food_data["foodId"]
            )
            food_obj.label = food_data["label"]
            food_obj.category = category
            food_obj.save()

            if is_importing:
                analyze_food_nutrients(food_obj.id)

            food_objs.append(food_obj)
        return food_objs
    else:
        print(food_name)
        return None


# A more in-depth analysis of food.
# Gives both macro- and micro- nutrients
# The food should have been analyzed before calling this function
def analyze_food_nutrients(food_id) -> None:
    # Any micronutrient will do, but not MACRONUTRIENT because they were created during parsing!
    if not FoodNutrient.objects.filter(food_id=food_id, nutrient_id="P"):
        # We are going to use 100g as a standard quantity for storing food in the database
        ingredients = {
            "ingredients": [
                {
                    "quantity": STANDARD_MEASURE_QUANTITY,
                    "measureURI": STANDARD_MEASURE_URI,
                    "foodId": food_id,
                }
            ]
        }
        # Gets the nutrition data
        nutrition_request = requests.post(NUTRIENTS_AP, json=ingredients).json()
        nutrients_data = nutrition_request["totalNutrients"]
        # Adds each food nutrient to the database
        food_nutrient_list = []
        for nutrient in Nutrient.objects.all():
            amount = 0
            if nutrient.id in nutrients_data:
                amount = nutrients_data[nutrient.id].get("quantity", 0)
            food_nutrient = FoodNutrient(
                food_id=food_id,
                nutrient=nutrient,
                amount=amount,
            )
            food_nutrient_list.append(food_nutrient)
        FoodNutrient.objects.bulk_create(food_nutrient_list)


# Analyze each food generated by chatGPT and import each food to the database (Caching the food)
# foods is a list of food dictionary
# Each dictionary is of the format {"food_name" : "", "food_portion": 200}
def analyze_meal_plan(food_dict_list, is_importing=False) -> list:
    food_obj_dict_list = []
    for food_dict in food_dict_list:
        food_objs = analyze_food(food_dict["food_name"], is_importing=is_importing)
        if food_objs:
            # Gets the first food that is returned by the database
            food = food_objs[0]
            food_obj_dict = {"food": food, "amount": food_dict["amount"]}
            food_obj_dict_list.append(food_obj_dict)
        else:
            continue
    return food_obj_dict_list


# Create the new user food entry in the database
# import means that we don't have to analyze the food
def import_user_food(user, food_obj_dict, date=datetime.now()):
    food = food_obj_dict["food"]
    daily_entry, created = DailyEntry.objects.get_or_create(user=user, date=date)
    if food:
        user_food = UserFood.objects.create(
            food=food, daily_entry=daily_entry, weight=food_obj_dict["amount"]
        )
        return user_food
    return


# Given food_dict_list and user, analyze each food and create a new instance of model
# Use this after you've asked gpt
# TODO: The longest part of import is probably analyzing the food. Optimize it.
def import_user_meal_plan(user, food_dict_list, date=datetime.now()):
    print(food_dict_list)
    food_obj_dict_list = analyze_meal_plan(food_dict_list, is_importing=True)
    for food_obj_dict in food_obj_dict_list:
        user_food = import_user_food(user, food_obj_dict, date)
        if not user_food:
            print("{0} doesn't exist!".format(food_obj_dict["food"]))
    return True


def get_exercise_data(params) -> list:
    return requests.get(
        EXERCISE_DB_EP, headers=EXERCISE_DB_HEADERS, params=params
    ).json()


# Call the api to obtain data about the exercise and also create instances of those exercises as StrengthExercise object
# Usually, multiple exercises will be returned from the api
# So, a list will be returned
def get_exercises(params) -> list:
    exercise_data_list = get_exercise_data(params)
    exercise_list = []
    for exercise_data in exercise_data_list:
        exercise = StrengthExercise(
            id=exercise_data["id"],
            name=exercise_data["exercise_name"],
            # difficulty=exercise_data["difficulty"],
            # category=exercise_data["Category"],
        )
        exercise_list.append(exercise)
    StrengthExercise.objects.bulk_create(exercise_list, ignore_conflicts=True)
    return exercise_list


# TODO
# Given a requesta dnd exercise schedule, import it into the database
def import_exercise_plan(request, exercise_schedule):
    user = request.user
    now = datetime.now()
    for i in range(len(exercise_schedule)):
        print(i)
        exercise_routine = exercise_schedule[i]
        if exercise_routine["is_rest_day"]:
            continue
        daily_entry_date = now + timedelta(i)
        daily_entry, _ = DailyEntry.objects.get_or_create(
            user=user, date=daily_entry_date
        )

        for exercise in exercise_routine["strength_exercises"]:
            params = {"name": exercise["exercise_name"]}
            exercise_obj = get_exercises(params)
            if exercise_obj:
                user_strength_exercise, _ = UserStrengthExercise.objects.get_or_create(
                    user=user,
                    daily_entry=daily_entry,
                    exercise=exercise_obj[0],
                    sets=exercise["sets"],
                    reps=exercise["reps"],
                )
            else:
                print("Exercise not found!")
    return True


# Given a list of dictionary of exercise names, sets, reps, create a context for rendering in html
def create_exercise_plan_context(exercise_schedule):
    # TODO: VIDEO
    for exercise_routine in exercise_schedule:
        for exercise in exercise_routine["strength_exercises"]:
            exercise_data = get_exercise_data({"name": exercise["exercise_name"]})
            if exercise_data:
                exercise.update({"videoURL": exercise_data[0]["videoURL"]})
    context = {
        "type": "exercise",
        "exercise_schedule": exercise_schedule,
        "vals": json.dumps(exercise_schedule),
    }
    return context


# Ask ChatGPT for the exercise plan
def ask_exercise_plan_gpt(user, time_available=60, exercise_type="Weight Lifting"):
    messages = [
        DEFAULT_SYSTEM_MESSAGE,
        {
            "role": "system",
            "content": "The exercise routine must fully specify the name of the exercise, the weight, number of reps, and number of sets. Also, specify the estimated time that it will take to finish. Make sure to include rest days in your response",
        },
        {
            "role": "system",
            "content": "I want to do {exercise_type} exercises.".format(
                exercise_type=exercise_type
            ),
        },
        {
            "role": "user",
            "content": "Recommend me a full week exercise schedule. Each session can completed within {time_available} minutes. Base your recommendation on the following information: {info}".format(
                time_available=time_available, info=user.info()
            ),
        },
    ]
    functions = [
        {
            "name": "create_exercise_plan_context",
            "description": "Given an array of exercise routine, create a context that is necessary for rendering html",
            "parameters": {
                "type": "object",
                "properties": {
                    "exercise_schedule": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "is_rest_day": {
                                    "type": "boolean",
                                    "description": "True if you don't have to do any exercise on that day",
                                },
                                "day_of_the_week": {
                                    "type": "string",
                                    "description": "Day of the week. Ex: Monday, Friday, Tuesday, etc.",
                                },
                                "warmup": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "exercise_name": {
                                                "type": "string",
                                                "description": "Name of the exercise",
                                            },
                                            "duration": {
                                                "type": "number",
                                                "description": "Time it takes to complete the exercise (in minutes)",
                                            },
                                        },
                                    },
                                },
                                "strength_exercises": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "exercise_name": {
                                                "type": "string",
                                                "description": "Name of the exercise",
                                            },
                                            "sets": {
                                                "type": "number",
                                                "description": "Number of sets",
                                            },
                                            "reps": {
                                                "type": "number",
                                                "description": "Number of reps",
                                            },
                                        },
                                    },
                                },
                                "cardio": {
                                    "type": "object",
                                    "properties": {
                                        "exercise_name": {
                                            "type": "string",
                                            "description": "Name of the exercise",
                                        },
                                        "duration": {
                                            "type": "number",
                                            "description": "Time it takes to complete the exercise (in minutes)",
                                        },
                                    },
                                    "description": "A list of exercises to do during cardio",
                                },
                                "cooldown": {
                                    "type": "object",
                                    "properties": {
                                        "exercise_name": {
                                            "type": "string",
                                            "description": "Name of the exercise",
                                        },
                                        "duration": {
                                            "type": "number",
                                            "description": "Time it takes to complete the exercise (in minutes)",
                                        },
                                    },
                                    "description": "Exercise to do during cooldown",
                                },
                            },
                        },
                    },
                },
                "required": ["exercise_schedule"],
            },
        }
    ]
    response = openai.ChatCompletion.create(
        model=GPT_MODEL_16K,
        messages=messages,
        functions=functions,
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        function_call={"name": "create_exercise_plan_context"},
    )
    response_message = response["choices"][0]["message"]

    if response_message.get("function_call"):
        function_name = response_message["function_call"]["name"]
        if (
            function_name == "create_exercise_plan_context"
            and response_message["function_call"]["arguments"] is not None
        ):
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_response = create_exercise_plan_context(
                exercise_schedule=function_args.get("exercise_schedule"),
            )
            return function_response

    return response_message["content"]


# Given a paragraph and a list of dictionary of food names, amounts, units, and calories, create a context that will be used in rendering
def create_meal_plan_context(paragraph, food_dict_list):
    context = {
        "type": "meal",
        "paragraph": paragraph,
        "food_dict_list": food_dict_list,
    }
    return context


# Ask ChatGPT for a meal plan given the user's information
# If successful a context for rendering in html is returned
@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def ask_meal_plan_gpt(user):
    messages = [
        DEFAULT_SYSTEM_MESSAGE,
        {
            "role": "user",
            "content": "Recommend me a delicious healthy meal plan that is not boring that contains a total of {tdeg} calories and splitted into {meal_frequency} meals. Give the portion in grams".format(
                tdeg=user.get_tdeg(), meal_frequency=user.meal_frequency
            ),
        },
    ]
    functions = [
        {
            "name": "create_meal_plan_context",
            "description": "Given a paragraph and a list of dictionary of food names, amounts, units, and calories, create a context for rendering in html",
            "parameters": {
                "type": "object",
                "properties": {
                    "paragraph": {
                        "type": "string",
                        "description": "A paragraph of what ChatGPT wants to say before recommending the meal plan",
                    },
                    "food_dict_list": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "food_name": {
                                    "type": "string",
                                    "description": "Name of the food",
                                },
                                "amount": {
                                    "type": "number",
                                    "description": "Amount of food",
                                },
                                "unit": {
                                    "type": "string",
                                    "description": "Weight unit",
                                },
                                "calories": {
                                    "type": "string",
                                    "description": "Total calories",
                                },
                            },
                        },
                    },
                },
                "required": ["paragraph", "food_dict_list"],
            },
        }
    ]
    # TODO: The 3.5 model does not recommend a satisfactory answer. It consistently recommends less than the specified calories. We will now use 4 instead, but first we need to use a total of $1
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
        functions=functions,
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    response_message = response["choices"][0]["message"]

    if response_message.get("function_call"):
        function_name = response_message["function_call"]["name"]
        if (
            function_name == "create_meal_plan_context"
            and response_message["function_call"]["arguments"] is not None
        ):
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_response = create_meal_plan_context(
                paragraph=function_args.get("paragraph"),
                food_dict_list=function_args.get("food_dict_list"),
            )
            return function_response

    return response_message["content"]


# Ask the ai to analyze the user's history and create a plan based on it
# The history is analyzed from the specified number of days in the past until the present.
# This is pricey. Don't run it often!
def ai_analyze_history(user, number_of_days):
    health_message = "Here is my fitness information: {info}".format(info=user.info())
    messages = [
        DEFAULT_SYSTEM_MESSAGE,
        {
            "role": "system",
            "content": "When I give you a history of food intake and exercises in the following python format (portion is in grams) (duration is in minutes):\n'''\n[\n{'d': '', 'i': [{'l': ''}], 'k':0, 'm': {'p':0, 'c': 0, 'f': 0}, 'e': [{'n': '', 's': 0, 'r': 0}]}\n]\n'''\nd stands for date\ni stands for food intake\nl stands for food name\ne stands for exercise\nn stands for exercise name\ns stands for number ofexercise sets\nr stands for number of exercise reps\nk stands for total calories intake\nm stands for macronutrients\np stands for protein\nc stands for carbohydrates\nf stands for total fats\nI want you to customly create an advice for me and tell me whether I hit my calories target and what are my errors. Make an overall summary. Don't list day by day.\n",
        },
        {
            "role": "system",
            "content": "I will also give you my health information. Make sure to base your advice on that too.",
        },
        {"role": "user", "content": health_message},
    ]
    history = []
    for daily_entry in DailyEntry.objects.filter(
        user=user, date__gt=(datetime.now() - timedelta(number_of_days))
    ):
        history.append(daily_entry.ai_summarize())
    messages.append({"role": "user", "content": str(history)})
    print(history)
    response = openai.ChatCompletion.create(
        model=GPT_MODEL_16K,
        messages=messages,
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    response_message = response["choices"][0]["message"]["content"]
    return response_message


# Edamam provides a convenient autocomplete functionality
# which can be implemented for use when searching for ingredients.
def autocomplete_search(search):
    # Maximum food names to be returned
    params = {"q": search}
    response = requests.get(AUTOCOMPLETE_AP, params=params)
    return json.loads(response.content)
