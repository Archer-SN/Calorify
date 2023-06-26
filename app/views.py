
from django.shortcuts import render
from django.shortcuts import HttpResponse

from .models import *

# This function handles the index page
# It just renders a html file
def index(request):
    daily_entry = DailyEntry.objects.create()
    food = Food.objects.get(fdc_id=2514746)
    user_food = UserFood.objects.create(food=food, daily_entry=daily_entry, amount=100)
    return HttpResponse(user_food.get_calories())

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


