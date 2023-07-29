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

# We are going to make a simulation of 180 days or 6 months
NUMBER_OF_DAYS = 180

HEALTHY_MEAL_PLAN_MESSAGE = (
    "Recommend me a healthy meal plan based on the following information: {info}"
)
RANDOM_MEAL_PLAN_MESSAGE = "Recommend me a meal plan that is composed of fast foods and is my calorie goal based on the following information: {info}"

# Simulate each account for 6 months each with different behavior.
# Some consistent, some inconsistent. Some users change their plans.

# Male 35 years old. Overweight. Not active and eats poorly.
# Does well in the first few weeks but after, loses motivation and false behind.
A1, _ = User.objects.get_or_create(
    username="A1",
    email="A1@gmail.com",
    sex="M",
    activity_level=User.ACTIVITY_LEVEL.SED,
    weight=90,
    height=175,
    date_born=datetime(1988, 1, 1),
    meal_frequency=3,
    recommendation_frequency=30,
)
A1.set_password("123")
A1.save()

# Same as profile A1 but can be easily motivated if results are good.
# Later changes goal.
A2, _ = User.objects.get_or_create(
    username="A2",
    email="A2@gmail.com",
    sex="M",
    activity_level=User.ACTIVITY_LEVEL.SED,
    weight=90,
    height=175,
    date_born=datetime(1988, 1, 1),
    meal_frequency=3,
    recommendation_frequency=30,
)
A2.set_password("123")
A2.save()

# Not overweight but high fat ratio.
# Lazy to workout but eats normal.
B1, _ = User.objects.get_or_create(
    username="B1",
    email="B1@gmail.com",
    sex="F",
    activity_level=User.ACTIVITY_LEVEL.SED,
    weight=60,
    height=165,
    date_born=datetime(1993, 1, 1),
    meal_frequency=3,
    recommendation_frequency=30,
    body_fat=33,
)
B1.set_password("123")
B1.save()

# Same as B1  Lazy to work out and doesn’t eat well.
B2, _ = User.objects.get_or_create(
    username="B2",
    email="B2@gmail.com",
    sex="F",
    activity_level=User.ACTIVITY_LEVEL.SED,
    weight=60,
    height=165,
    date_born=datetime(1993, 1, 1),
    meal_frequency=3,
    recommendation_frequency=30,
    body_fat=33,
)
B2.set_password("123")
B2.save()


easy_difficulty, _ = Difficulty.objects.get_or_create(name="Easy", xp=10, gems=5)
medium_difficulty, _ = Difficulty.objects.get_or_create(name="Medium", xp=50, gems=10)
hard_difficulty, _ = Difficulty.objects.get_or_create(name="Hard", xp=250, gems=15)
goggins_difficulty, _ = Difficulty.objects.get_or_create(
    name="Goggins", xp=9001, gems=9001
)


def create_challenge():
    easy_challenge = Challenge.objects.create(
        name="Drink 2L water", difficulty=easy_difficulty
    )

    medium_challenge = Challenge.objects.create(
        name="Run 2 miles", difficulty=medium_difficulty
    )

    hard_challenge = Challenge.objects.create(
        name="Weight training for 2 hours", difficulty=hard_difficulty
    )
    goggins_challenge = Challenge.objects.create(
        name="Run 100 miles", difficulty=goggins_difficulty
    )

    A1.challenge_set.add(easy_challenge)
    A1.challenge_set.add(medium_challenge)
    A1.challenge_set.add(hard_challenge)
    A1.challenge_set.add(goggins_challenge)


def create_daily_challenge():
    pass


def create_weekly_challenge():
    pass


def create_monthly_challenge():
    pass


def clear_daily_entry(user):
    DailyEntry.objects.filter(user=user).delete()


# TODO
def simulate_a1():
    # unhealthy_foods = [
    #     {"food_name": "pizza", "food_portion": 500},
    #     {"food_name": "Extra Crispy Chicken- Thigh", "food_portion": 500},
    #     {"food_name": "Pancake", "food_portion": 300},
    #     {"food_name": "Coke", "food_portion": 722},
    # ]
    for i in range(NUMBER_OF_DAYS + 1, 1, -1):
        pass
    print("A1 Simulation Done!")


# TODO
def simulate_a2():
    for i in range(NUMBER_OF_DAYS, 0, -1):
        pass
    print("A2 Simulation Done!")


# TODO
def simulate_b1():
    for i in range(NUMBER_OF_DAYS, 0, -1):
        pass
    print("B1 Simulation Done!")


# TODO
def simulate_b2():
    for i in range(NUMBER_OF_DAYS, 0, -1):
        pass
    print("B2 Simulation Done!")


def run():
    create_daily_challenge()
    create_challenge()
    simulate_a1()
    simulate_a2()
    simulate_b1()
    simulate_b2()


run()
