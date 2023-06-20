from django.db import models
from django.contrib.auth.models import AbstractUser

# A shorthand for each unit
UNIT_CHOICES = (("cm", "centimeters"), ("kg", "kilograms"), ("in", "inches"), ("ft", "feet"), ("lbs", "pounds"))

# This is a collection of unit conversion factors
# We convert from A -> B
unit_conversions = {
    ("ft", "cm"): 30.48,
    ("in", "cm"): 2.54,
    ("cm", "ft"): (1 / 30.48),
    ("cm", "in"): (1 / 2.54),
    ("kg", "lbs"): 2.205,
    ("lbs", "kg"): (1/2.205),
}


# Create your models here.

class User(AbstractUser):
    weight = models.FloatField()
    height = models.FloatField()


# Food class has data about the amount of calories, macronutrients, and nutrients.
class Food(models.Model):
    pass


# A collection of Food
class Recipe(models.Model):
    pass


# DailyEntry contains information about your total calories intake for the day, exercised, etc.
class DailyEntry(models.Model):
    pass
