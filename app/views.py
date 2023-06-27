
from django.shortcuts import render
from django.shortcuts import HttpResponse

from datetime import datetime
from .models import *

# This function handles the index page
# It just renders a html file
def index(request):
    user, created = User.objects.get_or_create(username="RAM", email="ram314@gmail.com", weight=78, height=176, body_fat=20, year_born=datetime(2000, 1, 1))
    if created:
        user.set_password(123)
        user.save()
    daily_entry = DailyEntry.objects.create()
    foods = Food.objects.all()[0:10]
    x = 10
    for food in foods:
        UserFood.objects.create(food=food, daily_entry=daily_entry, amount=x)
        x += 10

    return HttpResponse(daily_entry.get_calories())

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


