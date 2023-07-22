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

HEALTHY_MEAL_PLAN_MESSAGE = (
    "Recommend me a healthy meal plan based on the following information: {info}"
)
RANDOM_MEAL_PLAN_MESSAGE = "Recommend me a meal plan that is composed of fast foods and is my calorie goal based on the following information: {info}"

# Here is the information of each user
# All users have the same health information but with different account age
# User1 : 0 month
# User2 : 1 month
# User3 : 3 months
# User4 : 6 months

user1, _ = User.objects.get_or_create(
    username="User1",
    email="a@gmail.com",
    sex="M",
    activity_level=User.ACTIVITY_LEVEL.MA,
    weight="75",
    height="175",
    date_born=datetime(2006, 6, 15),
    meal_frequency=3,
    recommendation_frequency=30,
    first_name="Extraordinary",
    last_name="Person",
)
user1.set_password("123")

user2, _ = User.objects.get_or_create(
    username="User2",
    email="b@gmail.com",
    sex="M",
    activity_level=User.ACTIVITY_LEVEL.MA,
    weight="75",
    height="175",
    date_born=datetime(2006, 6, 15),
    meal_frequency=3,
    recommendation_frequency=30,
    first_name="Extraordinary",
    last_name="Person",
)
user2.set_password("123")

user3, _ = User.objects.get_or_create(
    username="User3",
    email="c@gmail.com",
    sex="M",
    activity_level=User.ACTIVITY_LEVEL.MA,
    weight="100",
    height="170",
    date_born=datetime(1987, 4, 1),
    meal_frequency=5,
    recommendation_frequency=30,
    first_name="Obese",
    last_name="Person",
)
user3.set_password("123")


def create_difficulties():
    easy_difficulty = Difficulty.objects.create(name="Easy", xp=10, gems=5)
    medium_difficulty = Difficulty.objects.create(name="Medium", xp=50, gems=10)
    hard_difficulty = Difficulty.objects.create(name="Hard", xp=250, gems=15)
    goggins_difficulty = Difficulty.objects.create(name="Goggins", xp=9001, gems=9001)


def create_challenge():
    easy_challenge = Challenge.objects.create("Drink 2L water")
    user1.challenge


def create_daily_challenge():
    pass


def create_weekly_challenge():
    pass


def create_monthly_challenge():
    pass


def clear_daily_entry(user):
    DailyEntry.objects.filter(user=user).delete()


def simulate_user1():
    message = {
        "role": "user",
        "content": RANDOM_MEAL_PLAN_MESSAGE.format(info=user1.info()),
    }
    unhealthy_foods = [
        {"food_name": "pizza", "food_portion": 500},
        {"food_name": "Extra Crispy Chicken- Thigh", "food_portion": 500},
        {"food_name": "Pancake", "food_portion": 300},
        {"food_name": "Coke", "food_portion": 722},
    ]
    for i in range(NUMBER_OF_DAYS + 1, 1, -1):
        meal_plan = analyze_meal_plan(unhealthy_foods)

        print(import_user_meal_plan(user1, meal_plan, datetime.now() - timedelta(i)))

    print("User1 Done!")


def simulate_user2():
    healthy_foods = {
        "foods": [
            {"food_name": "lean chicken breast", "food_portion": 120},
            {"food_name": "sweet potato", "food_portion": 150},
            {"food_name": "broccoli", "food_portion": 100},
            {"food_name": "salmon", "food_portion": 150},
            {"food_name": "quinoa", "food_portion": 100},
            {"food_name": "mixed greens", "food_portion": 150},
            {"food_name": "tofu", "food_portion": 100},
            {"food_name": "brown rice", "food_portion": 200},
            {"food_name": "stir-fried vegetables", "food_portion": 100},
        ]
    }

    for i in range(NUMBER_OF_DAYS, 0, -1):
        meal_plan = analyze_meal_plan(healthy_foods)
        print(
            import_user_meal_plan(user2, meal_plan, date=datetime.now() - timedelta(i))
        )
    print("User2 Done!")


def simulate_user3():
    for i in range(NUMBER_OF_DAYS, 0, -1):
        pass


def run():
    create_difficulties()
    create_daily_challenge()
    # simulate_user1_inconsistent()
    # simulate_user1_consistent()
    # simulate_user2()
    # simulate_user3()
    # simulate_user4()
    # ai_analyze_history(user1_inconsistent, NUMBER_OF_DAYS)
    # ai_analyze_history(user1_consistent, NUMBER_OF_DAYS)


run()
