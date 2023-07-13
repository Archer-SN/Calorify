from app.models import *

from datetime import datetime

import openai
import json
import requests

# We are going to make a simulation of 30 days

# Simulate User1 activities
user1 = User.objects.get_or_create(username="User1", email="a@gmail.com", password="123", sex="M", activity_level="MA",
                                   weight="75", height="173", year_born=datetime(2006, 6, 15), meal_frequency=3,
                                   recommendation_frequency=30, first_name="Siwakorn", last_name="Sukchomthong")

# Simulate User2 activities
user2 = User.objects.get_or_create(username="User2", email="b@gmail.com", password="123", sex="M", activity_level="SED",
                                   weight="120", height="170", year_born=datetime(1996, 7, 12), meal_frequency=5,
                                   recommendation_frequency=30, first_name="John", last_name="Doe")

# Simulate User3 activities
user3 = User.objects.get_or_create(username="User3", email="c@gmail.com", password="123", sex="F", activity_level="MA",
                                   weight="45", height="155", year_born=datetime(1993, 7, 12), meal_frequency=2,
                                   recommendation_frequency=30, first_name="Jane", last_name="Doe")
# Simulate User4 activities
user4 = User.objects.get_or_create(username="User4", email="d@gmail.com", password="123", sex="M", activity_level="VA",
                                   weight="90", height="185", year_born=datetime(1975, 2, 17), meal_frequency=1,
                                   recommendation_frequency=30, first_name="David", last_name="Goggins")
