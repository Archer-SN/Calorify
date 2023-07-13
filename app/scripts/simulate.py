from datetime import datetime

import openai
import json
import requests
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calorify.settings")
django.setup()

from app.models import *
from app.api import *

# We are going to make a simulation of 30 days
NUMBER_OF_DAYS = 30


# Create all the users
def user_setup():
    user1, _ = User.objects.get_or_create(username="User1", email="a@gmail.com", sex="M",
                                          activity_level=User.ACTIVITY_LEVEL.MA,
                                          weight="75", height="175", year_born=datetime(2006, 6, 15), meal_frequency=3,
                                          recommendation_frequency=30, first_name="FakeSiwakorn",
                                          last_name="NotSukchomthong")
    user1.set_password("123")

    user2, _ = User.objects.get_or_create(username="User2", email="b@gmail.com", sex="M",
                                          activity_level=User.ACTIVITY_LEVEL.SED,
                                          weight="120", height="170", year_born=datetime(1996, 7, 12), meal_frequency=5,
                                          recommendation_frequency=30, first_name="John", last_name="Doe")
    user2.set_password("123")

    user3, _ = User.objects.get_or_create(username="User3", email="c@gmail.com", sex="F",
                                          activity_level=User.ACTIVITY_LEVEL.MA,
                                          weight="45", height="155", year_born=datetime(1993, 7, 12), meal_frequency=2,
                                          recommendation_frequency=30, first_name="Jane", last_name="Doe")
    user3.set_password("123")

    user4, _ = User.objects.get_or_create(username="User4", email="d@gmail.com", sex="M",
                                          activity_level=User.ACTIVITY_LEVEL.VA,
                                          weight="90", height="185", year_born=datetime(1975, 2, 17), meal_frequency=1,
                                          recommendation_frequency=30, first_name="David", last_name="Goggins")
    user4.set_password("123")


def simulate_user1():
    for i in range(1, NUMBER_OF_DAYS + 1):
        pass

def simulate_user2():
    pass


def simulate_user3():
    pass


def simulate_user4():
    pass

def run():
    # user_setup()
    simulate_user1()
    simulate_user2()
    simulate_user3()
    simulate_user4()

run()