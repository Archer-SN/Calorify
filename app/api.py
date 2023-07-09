"""
This file will handle the logic of communicating with API such as EDAMAM, ChatGPT, etc.
"""

from .scripts import credentials
from .models import *

import openai
import json
import requests

openai.api_key = credentials.OPEN_AI_KEY

GPT_MODEL = "gpt-3.5-turbo"

# Id and Keys for the food database api
EDAMAM_FOOD_DB_ID = "35db61c2"
EDAMAM_FOOD_DB_KEY = credentials.EDAMAM_FOOD_DB_KEY

# AP stands for Access Point
# The parser access point handles text search for foods as well as filters for the foods like presence specific nutrient content or exclusion of allergens.
PARSER_AP = "https://api.edamam.com/api/food-database/v2/parser?app_id={app_id}&app_key={app_key}".format(
    app_id=EDAMAM_FOOD_DB_ID, app_key=EDAMAM_FOOD_DB_KEY)

# In the response to your parser request you receive the a food ID for each database match.
# Using the food ID and the measure URI, which parser provides, you can make a request to the nutrients access point.
# The nutrients access points returns nutrition with diet and health labels for a given quantity of the food.
NUTRIENTS_AP = "https://api.edamam.com/api/food-database/v2/nutrients?app_id={app_id}&app_key={app_key}".format(
    app_id=EDAMAM_FOOD_DB_ID, app_key=EDAMAM_FOOD_DB_KEY)

# Id and keys for the recipe database api
EDAMAM_RECIPE_DB_ID = "c03ec76f"
EDAMAM_RECIPE_DB_KEY = credentials.EDAMAM_RECIPE_DB_KEY

# Id and keys for the nutrients analysis api
EDAMAM_NUTRIENTS_ANALYSIS_ID = "8f60cfad"
EDAMAM_NUTRIENTS_ANALYSIS_KEY = credentials.EDAMAM_NUTRIENTS_ANALYSIS_KEY

STANDARD_MEASURE_UNIT = "g"
STANDARD_MEASURE_URI = "http://www.edamam.com/ontologies/edamam.owl#Measure_gram"
STANDARD_MEASURE_QUANTITY = 100


# I'm not sure whether this should be put in views.py

# Add the given food to the database if it does not yet exist
# food_name is a string that has the format "{amount} {unit} {food}"
# We'll call the database with the food weight of 100 grams (A standard weight for storing in the database)
# Return the UserFood that is created
def create_user_food(user, food_name):
    parser_params = {"ingr": food_name}
    # Calls the database api to obtain list of foods
    parser_request = requests.get(PARSER_AP, params=parser_params).json()
    # Gets the first food that is returned from the API call
    data = parser_request["parsed"][0]
    food_data = data["food"]
    category, category_created = FoodCategory.objects.get_or_create(description=food_data["category"])
    food, food_created = Food.objects.get_or_create(food_id=food_data["foodId"], label=food_data["label"],
                                                    food_category=category)
    if not food_created:
        # We are going to use 100g as a standard quantity for storing food in the database
        ingredients = {
            "ingredients": [
                {
                    "quantity": STANDARD_MEASURE_QUANTITY,
                    "measureURI": STANDARD_MEASURE_URI,
                    "foodId": food_data["foodId"]
                }
            ]
        }
        # Gets the nutrition data
        nutrition_request = requests.post(NUTRIENTS_AP, json=ingredients).json()
        # Adds each nutrient to the database
        for ntr_code, nutrient_data in nutrition_request["totalNutrients"].items():
            nutrient, nutrient_created = Nutrient.objects.get_or_create(ntr_code=ntr_code, label=nutrient_data["label"],
                                                                        unit_name=nutrient_data["unit"])
            food_nutrient = FoodNutrient.objects.create(food=food, nutrient=nutrient, amount=nutrient_data["quantity"])
    # The total food weight in grams
    total_weight = data["quantity"] * data["measure"]["weight"]
    daily_entry, created = DailyEntry.objects.get_or_create(user=user)
    # Actually create the UserFood object so that we can get the real total nutrients
    user_food = UserFood.objects.create(food=food, daily_entry=daily_entry, weight=total_weight)
    return user_food


# Import the chat gpt generated meal plan into the database
# foods is a list of strings of food that has the format "{amount} {unit} {food}"
def import_meal_plan(user, foods):
    for food_name in foods:
        create_user_food(user, food_name)


def import_routine_plan():
    pass


# Ask ChatGPT for a meal plan given the user's information
def ask_meal_plan_gpt(user):
    messages = [{
        "role": "system",
        "content": "You are an expert in cooking and fitness. When I give you a list of ingredients and their quantities, you must create a meal plan based on those ingredients using no more than the given quantities. You can use any ingredient other than the given. If no ingredients are given, use anything you want. You don't need to specify the total calories. Don't list the instructions unless otherwise specificed. Take your time."
    },
        {"role": "user",
         "content": "Generate a healthy and tasty meal plan that has a total of {tdee} calories.".format(
             tdee=user.get_tdee())}]
    functions = [{
        "name": "import_meal_plan",
        "description": "Given a list of foods and its portion, import it to the database",
        "parameters": {
            "type": "object",
            "properties": {
                "foods": {
                    "type": "object",
                    "description": "A list of foods with portion in the front",
                },
                "user": {
                    "type": "object"
                }
            },
            "required": ["foods"],
        },
    }]
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
        functions=functions,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    response_message = response["choices"][0]["message"]

    # Check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        print("function not yet called")
        available_functions = {
            "import_meal_plan": import_meal_plan,
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        if function_name not in available_functions:
            return

        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_to_call(foods=function_args.get("foods"), user=user)
        print("fnction called")

    print("Hello")
    return response.choices[0].message
