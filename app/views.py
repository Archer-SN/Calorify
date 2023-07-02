from .scripts import credentials

from django.shortcuts import render
from django.shortcuts import HttpResponse
import requests
import json

from datetime import datetime
from .models import *

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
NUTRIENTS_AP = "https://api.edamam.com/api/food-database/v2/nutrients"

# Id and keys for the recipe database api
EDAMAM_RECIPE_DB_ID = "c03ec76f"
EDAMAM_RECIPE_DB_KEY = credentials.EDAMAM_RECIPE_DB_KEY


# A page for testing functionalities
def test(request):
    user, created = User.objects.get_or_create(username="RAM", email="ram314@gmail.com", weight=78, height=176,
                                               body_fat=20, year_born=datetime(2000, 1, 1))
    if created:
        user.set_password("123")
        user.save()
    daily_entry = DailyEntry.objects.create(user=user)
    r = requests.get(
        PARSER_AP + "&ingr={food_name}&nutrition-type=cooking".format(food_name="banana")).json()

    banana_data = r["parsed"][0]["food"]
    energy, created = Nutrient.objects.get_or_create(name="ENERC_KCAL", unit_name="kcal")
    banana, created = Food.objects.get_or_create(food_id=banana_data["foodId"], label=banana_data["label"])
    try:
        food_nutrient, created = FoodNutrient.objects.get_or_create(food=banana, nutrient=energy, amount=89)
    except:
        pass
    UserFood.objects.create(daily_entry=daily_entry, food=banana, amount=100)
    UserFood.objects.create(daily_entry=daily_entry, food=banana, amount=100)
    return HttpResponse(daily_entry.total_calories())


# This function handles the index page
# It just renders a html file
def index():
    pass


# Renders the login page
def login():
    pass


# Renders the register page
def register():
    pass


# Renders the error page
def error():
    pass


# Renders the diary page
def diary():
    pass
