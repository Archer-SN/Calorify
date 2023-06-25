
from django.shortcuts import render
from django.shortcuts import HttpResponse

from .models import *

# This function handles the index page
# It just renders a html file
def index(request):
    return HttpResponse(Nutrient.objects.all())

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


