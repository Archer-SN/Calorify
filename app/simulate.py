from datetime import datetime, timedelta

import openai
import json
import requests
import os
import django

# Must come before the import statements below
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calorify.settings")
django.setup()

from app.api import *
from app.models import *

# We are going to make a simulation of 30 days
NUMBER_OF_DAYS = 30

HEALTHY_MEAL_PLAN_MESSAGE = "Recommend me a healthy meal plan based on the following information: {info}"
RANDOM_MEAL_PLAN_MESSAGE = "Recommend me a meal plan that is unhealthy based on the following information: {info}"

user1_inconsistent, _ = User.objects.get_or_create(username="User1_in", email="a@gmail.com", sex="M",
                                                   activity_level=User.ACTIVITY_LEVEL.MA,
                                                   weight="75", height="175", date_born=datetime(2006, 6, 15),
                                                   meal_frequency=3,
                                                   recommendation_frequency=30, first_name="Inconsistent",
                                                   last_name="Person")
user1_inconsistent.set_password("123")

user1_consistent, _ = User.objects.get_or_create(username="User1_con", email="ab@gmail.com", sex="M",
                                                 activity_level=User.ACTIVITY_LEVEL.MA,
                                                 weight="75", height="175", date_born=datetime(2006, 6, 15),
                                                 meal_frequency=3,
                                                 recommendation_frequency=30, first_name="Consistent",
                                                 last_name="Person")
user1_consistent.set_password("123")

user2, _ = User.objects.get_or_create(username="User2", email="b@gmail.com", sex="M",
                                      activity_level=User.ACTIVITY_LEVEL.SED,
                                      weight="120", height="170", date_born=datetime(1996, 7, 12), meal_frequency=5,
                                      recommendation_frequency=30, first_name="John", last_name="Doe")
user2.set_password("123")

user3, _ = User.objects.get_or_create(username="User3", email="c@gmail.com", sex="F",
                                      activity_level=User.ACTIVITY_LEVEL.MA,
                                      weight="45", height="155", date_born=datetime(1993, 7, 12), meal_frequency=2,
                                      recommendation_frequency=30, first_name="Jane", last_name="Doe")
user3.set_password("123")

user4, _ = User.objects.get_or_create(username="User4", email="d@gmail.com", sex="M",
                                      activity_level=User.ACTIVITY_LEVEL.VA,
                                      weight="90", height="185", date_born=datetime(1975, 2, 17), meal_frequency=1,
                                      recommendation_frequency=30, first_name="David", last_name="Goggins")
user4.set_password("123")


def create_daily_challenge():
    pass


def create_weekly_challenge():
    pass


def create_monthly_challenge():
    pass


def simulate_user1_inconsistent():
    message = {"role": "user", "content": RANDOM_MEAL_PLAN_MESSAGE.format(info=user1_inconsistent.info())}
    for i in range(NUMBER_OF_DAYS, 0, -1):
        meal_plan = ask_meal_plan_gpt(user1_inconsistent, message)
        print("inconsistent " + str(i))
        print(import_user_meal_plan(
            user1_inconsistent, meal_plan, date=datetime.now() - timedelta(i)))
    print("User1 Inconsistent Done!")


def simulate_user1_consistent():
    message = {"role": "user", "content": HEALTHY_MEAL_PLAN_MESSAGE.format(info=user1_consistent.info())}
    for i in range(NUMBER_OF_DAYS, 0, -1):
        meal_plan = ask_meal_plan_gpt(user1_consistent, message)
        print("consistent" + str(i))
        print(import_user_meal_plan(user1_consistent, meal_plan,
                                    date=datetime.now() - timedelta(i)))
    print("User1 Consistent Done!")


def simulate_user2():
    for i in range(NUMBER_OF_DAYS, 0, -1):
        pass


def simulate_user3():
    for i in range(NUMBER_OF_DAYS, 0, -1):
        pass


def simulate_user4():
    for i in range(NUMBER_OF_DAYS, 0, -1):
        pass


def run():
    # simulate_user1_inconsistent()
    # simulate_user1_consistent()
    # simulate_user2()
    # simulate_user3()
    # simulate_user4()
    ai_analyze_history(user1_inconsistent, NUMBER_OF_DAYS)
    ai_analyze_history(user1_consistent, NUMBER_OF_DAYS)



run()
