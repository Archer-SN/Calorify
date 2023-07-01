from .scripts import credentials

from django.shortcuts import render
from django.shortcuts import HttpResponse
import requests
import json

from datetime import datetime
from .models import *

# Id and Keys for the food database api
EDAMAM_APP_ID = "35db61c2"
EDAMAM_KEY = credentials.EDAMAM_KEY


# This function handles the index page
# It just renders a html file
def index(request):
    user, created = User.objects.get_or_create(username="RAM", email="ram314@gmail.com", weight=78, height=176,
                                               body_fat=20, year_born=datetime(2000, 1, 1))
    if created:
        user.set_password("123")
        user.save()
    daily_entry = DailyEntry.objects.create(user=user)
    r = requests.get(
        "https://api.edamam.com/api/food-database/v2/parser?app_id={app_id}&app_key={app_key}&ingr={food_name}&nutrition-type=cooking".format(
            app_id=EDAMAM_APP_ID, app_key=EDAMAM_KEY, food_name="banana")).json()

    banana_data = r["parsed"][0]["food"]
    energy, created = Nutrient.objects.get_or_create(name="ENERC_KCAL", unit_name="kcal")
    banana, created = Food.objects.get_or_create(food_id=banana_data["foodId"], label=banana_data["label"])
    food_nutrient, created = FoodNutrient.objects.get_or_create(food=banana, nutrient=energy, amount=89)
    UserFood.objects.get_or_create(daily_entry=daily_entry, food=banana, amount=100)
    return HttpResponse(daily_entry.total_calories())


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
