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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calorify.settings")
django.setup()

from .scripts.credentials import *
from .models import *

openai.api_key = OPEN_AI_KEY

GPT_MODEL = "gpt-3.5-turbo"
# Similar to the above model but can accept more text input
GPT_MODEL_16K = "gpt-3.5-turbo-16k"

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
AUTOCOMPLETE_AP = "https://api.edamam.com/auto-complete?app_id={app_id}&app_key={app_key}".format(
    app_id=EDAMAM_FOOD_DB_ID, app_key=EDAMAM_FOOD_DB_KEY
)

# Id and keys for the recipe database api
EDAMAM_RECIPE_DB_ID = "c03ec76f"
EDAMAM_RECIPE_DB_KEY = EDAMAM_RECIPE_DB_KEY

# Id and keys for the nutrients analysis api
EDAMAM_NUTRIENTS_ANALYSIS_ID = "8f60cfad"
EDAMAM_NUTRIENTS_ANALYSIS_KEY = EDAMAM_NUTRIENTS_ANALYSIS_KEY

STANDARD_MEASURE_UNIT = "g"
STANDARD_MEASURE_URI = "http://www.edamam.com/ontologies/edamam.owl#Measure_gram"
STANDARD_MEASURE_QUANTITY = 100

DEFAULT_SYSTEM_MESSAGE = {
    "role": "system",
    "content": "Assistant is an intelligent chatbot designed to help users answer health and fitness related questions. Given each user's data, your advice should be customly made for them. Be concise with your advice. Make sure the food that you give exists in the EDAMAM database.",
}


# I'm not sure whether this should be put in views.py


# Add the given food to the database if it does not yet exist
# We'll call the database with the food weight of 100 grams (A standard weight for storing in the database)
# Return a Food object that is created
def analyze_food(food_name):
    parser_params = {"ingr": food_name}
    # Calls the database api to obtain list of foods
    parser_request = requests.get(PARSER_AP, params=parser_params)
    parser_response = parser_request.json()
    if parser_request.status_code == 200:
        if len(parser_response["parsed"]) == 0:
            return None
        food_objs = []
        # Loop through all the data that is returned from the API call
        for data in parser_response["parsed"]:
            food_data = data["food"]
            category, category_created = FoodCategory.objects.get_or_create(
                description=food_data["category"]
            )
            # Create the food object if it does not yet exist
            food_obj, food_obj_created = Food.objects.get_or_create(
                food_id=food_data["foodId"]
            )
            food_obj.label = food_data["label"]
            food_obj.category = category
            food_obj.save()
            if not food_obj_created:
                # We are going to use 100g as a standard quantity for storing food in the database
                ingredients = {
                    "ingredients": [
                        {
                            "quantity": STANDARD_MEASURE_QUANTITY,
                            "measureURI": STANDARD_MEASURE_URI,
                            "foodId": food_data["foodId"],
                        }
                    ]
                }
                # Gets the nutrition data
                nutrition_request = requests.post(NUTRIENTS_AP, json=ingredients).json()
                # Adds each nutrient to the database
                for ntr_code, nutrient_data in nutrition_request["totalNutrients"].items():
                    nutrient, nutrient_created = Nutrient.objects.get_or_create(
                        ntr_code=ntr_code,
                        label=nutrient_data["label"],
                        unit_name=nutrient_data["unit"],
                    )
                    food_nutrient = FoodNutrient.objects.create(
                        food=food_obj, nutrient=nutrient, amount=nutrient_data["quantity"]
                    )
            food_objs.append(food_obj)

        return food_objs
    else:
        print(food_name)
        return None


# Analyze each food generated by chatGPT and import each food to the database (Caching the food)
# foods is a list of food dictionary
# Each dictionary is of the format {"food_name" : "", "food_portion": 200}
def analyze_meal_plan(food_dict_list):
    food_obj_dict_list = []
    for food_dict in food_dict_list:
        # Gets the first food that is returned by the database
        food = analyze_food(food_dict["food_name"])[0]
        food_obj_dict = {"food": food, "food_portion": food_dict["food_portion"]}
        food_obj_dict_list.append(food_obj_dict)
    return food_obj_dict_list


# Create the new user food entry in the database
# import means that we don't have to analyze the food
def import_user_food(user, food_obj_dict, date=datetime.now()):
    food = food_obj_dict["food"]
    daily_entry, created = DailyEntry.objects.get_or_create(user=user, date=date)
    if food:
        user_food = UserFood.objects.create(
            food=food, daily_entry=daily_entry, weight=food_obj_dict["food_portion"]
        )
        return user_food
    return


# Given a list of Food objects and their portions, use it to create UserFood objects
def import_user_meal_plan(user, food_obj_dict_list, date=datetime.now()):
    if not food_obj_dict_list:
        return
    for food_obj_dict in food_obj_dict_list:
        user_food = import_user_food(user, food_obj_dict, date)
        if not user_food:
            print("{0} doesn't exist!".format(food_obj_dict["food"]))
    return DailyEntry.objects.get(user=user, date=date).total_nutrients()


def import_routine_plan():
    pass


# Edamam provides a convenient autocomplete functionality
# which can be implemented for use when searching for ingredients.
def autocomplete_search(search):
    # Maximum food names to be returned
    limit = 5
    params = {"q": search, "limit": limit}
    return requests.get(AUTOCOMPLETE_AP, params=params).json()


# Ask ChatGPT for a meal plan given the user's information
# food_obj_list is returned
@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def ask_meal_plan_gpt(user, message):
    messages = [DEFAULT_SYSTEM_MESSAGE, message]
    functions = [
        {
            "name": "analyze_meal_plan",
            "description": "Call the food database to obtain food nutrients for each food",
            "parameters": {
                "type": "object",
                "properties": {
                    "food_dict_list": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "food_name": {"type": "string"},
                                "food_portion": {
                                    "type": "number",
                                    "description": "amount of food in grams",
                                },
                            },
                        },
                        "description": "A list of foods.",
                    }
                },
                "required": ["food_dict_list"],
            },
        }
    ]
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
        functions=functions,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        function_call={"name": "analyze_meal_plan"},
    )
    response_message = response["choices"][0]["message"]

    # Check if GPT wanted to call a function
    if response_message.get("function_call"):
        function_name = response_message["function_call"]["name"]
        if (
            function_name == "analyze_meal_plan"
            and response_message["function_call"]["arguments"] is not None
        ):
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_response = analyze_meal_plan(
                food_dict_list=function_args.get("food_dict_list")
            )
            return function_response

    return


# Ask the ai to analyze the user's history and create a plan based on it
# The history is analyzed from the specified number of days in the past until the present.
# This is pricey. Don't run it often!
def ai_analyze_history(user, number_of_days):
    health_message = "Here is my fitness information: {info}".format(info=user.info())
    messages = [
        DEFAULT_SYSTEM_MESSAGE,
        {
            "role": "system",
            "content": "When I give you a history of food intake and exercises in the following python format (portion is in grams) (duration is in minutes):\n'''\n[\n{'d': '', 'i': [{'l': ''}], 'k':0, 'm': {'p':0, 'c': 0, 'f': 0}, 'e': [{'n': '', 't': 0}]}\n]\n'''\nd stands for date\ni stands for food intake\nl stands for food name\ne stands for exercise\nn stands for exercise name\nt stands for exercise duration\nk stands for total calories intake\nm stands for macronutrients\np stands for protein\nc stands for carbohydrates\nf stands for total fats\nI want you to customly create an advice for me and tell me whether I hit my calories target and what are my errors. Make an overall summary. Don't list day by day.\n",
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
    response_message = response["choices"][0]["message"]
    print(response_message)
    return response_message
