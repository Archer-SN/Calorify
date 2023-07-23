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
user1.save()

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
user2.save()

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
user3.save()

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
    
    user1.challenge_set.add(easy_challenge)
    user1.challenge_set.add(medium_challenge)
    user1.challenge_set.add(hard_challenge)
    user1.challenge_set.add(goggins_challenge)
    user2.challenge_set.add(easy_challenge)
    user2.challenge_set.add(medium_challenge)
    user2.challenge_set.add(hard_challenge)
    user2.challenge_set.add(goggins_challenge)


def create_daily_challenge():
    pass


def create_weekly_challenge():
    pass


def create_monthly_challenge():
    pass


def clear_daily_entry(user):
    DailyEntry.objects.filter(user=user).delete()


def simulate_user1():
    unhealthy_foods = [
        {"food_name": "pizza", "food_portion": 500},
        {"food_name": "Extra Crispy Chicken- Thigh", "food_portion": 500},
        {"food_name": "Pancake", "food_portion": 300},
        {"food_name": "Coke", "food_portion": 722},
    ]
    for i in range(NUMBER_OF_DAYS + 1, 1, -1):
        print(import_user_meal_plan(user1, str(unhealthy_foods, datetime.now() - timedelta(i)))

    print("User1 Done!")


def simulate_user2():
    healthy_foods = [
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
    

    for i in range(NUMBER_OF_DAYS, 0, -1):
        print(
            import_user_meal_plan(user2, str(healthy_foods), date=datetime.now() - timedelta(i))
        )
    print("User2 Done!")


def simulate_user3():
    for i in range(NUMBER_OF_DAYS, 0, -1):
        pass


def run():
    create_daily_challenge()
    create_challenge()
    simulate_user1()
    simulate_user2


run()
