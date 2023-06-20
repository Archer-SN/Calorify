
from django.shortcuts import render
from django.shortcuts import HttpResponse

from .models import *

# This function handles the index page
# It just renders a html file
def index(request):
    return HttpResponse("Hello")

def login():
    pass

def register():
    pass

def diary():
    pass

