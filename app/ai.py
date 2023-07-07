"""
This file will handle all the logic for communicating with ChatGPT
ChatGPT is connected through API
"""

from scripts import credentials
from models import *

import openai
import json
import requests

openai.api_key = credentials.OPEN_AI_KEY

MODEL = "gpt-3.5-turbo"

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

# Add the given food to the database
# food_name is a string that has the format "{amount} {unit} {food}"
# We'll call the database with the food weight of 100 grams (A standard weight for storing in the database)
def add_food(food_name):
    parser_params = {"ingr": food_name}
    # Calls the database api to obtain list of foods
    parser_request = requests.get(PARSER_AP, params=parser_params).json()
    # Gets the first food that is returned from the API call
    data = parser_request["parsed"][0]
    food_data = data["food"]
    category, category_created = FoodCategory.objects.get_or_create(description=food_data["category"])
    food, food_created = Food.objects.get_or_create(food_id=food_data["foodId"], label=food_data["label"],
                                                    category=category)
    # We are going to use 100g as a standard quantity for storing food in the database
    nutrition_params = {"ingredients": {
        "ingredients": [
            {
                "quantity": STANDARD_MEASURE_QUANTITY,
                "measureURI": STANDARD_MEASURE_URI,
                "foodId": food_data["foodId"]
            }
        ]
    }}
    # Gets the nutrition data
    nutrition_request = requests.get(NUTRIENTS_AP, params=nutrition_params).json()
    # TODO Find a way to add daily_entry
    user_food = UserFood.objects.create(food=food, daily_entry=None, weight=nutrition_request["totalWeight"])
    # Adds each nutrient to the database
    for ntr_code, nutrient_data in nutrition_request["totalNutrients"].items():
        nutrient, nutrient_created = Nutrient.objects.get_or_create(ntr_code=ntr_code, label=nutrient_data["label"],
                                                                    unit_name=nutrient_data["unit"])
        food_nutrient = FoodNutrient.objects.create(food=food, nutrient=nutrient, amount=nutrient_data["quantity"])


# Given a dictionary of food, analyze its nutrition by calling the food database
def analyze_meal_plan(foods):
    pass


# Import the chat gpt generated meal plan into the database
# foods is a list of strings of food that has the format "{amount} {unit} {food}"
def import_meal_plan(foods):
    for food_name in foods:
        add_food(food_name)


def import_routine_plan():
    pass
