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
    ("in", "ft"): (1/12),
    ("ft", "in"): 12,
    ("cm", "m"): (1/100),
    ("m", "cm"): 100,
}

# Create your models here.

class User(AbstractUser):
    # This will be multiplied to BMR which will give TDEE
    NONE = 1
    SEDENTARY = 1.2
    LIGHT = 1.35
    MODERATE = 1.5
    VERY = 1.9
    ACTIVITY_LEVEL = [
        (NONE, "None"),
        (SEDENTARY, "Sedentary"),
        (LIGHT, "Lightly Active"),
        (MODERATE, "Moderately Active"),
        (VERY, "Very Active"),
        # TODO
        (1, "Custom"),
    ]

    SEX_CHOICES = [("M", "Male"), ("F", "Female")]
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)

    # Store weight in kg
    weight = models.IntegerField()
    # Store height in cm
    height = models.IntegerField()
    body_fat = models.FloatField()
    activity_level = models.IntegerField()


    def to_lbs(self):
        return round(self.weight * unit_conversions[("kg", "lbs")])

    # Convert the user height from cm to f
    def to_ft_in(self):
        # Convert height from centimeters to feet
        height_in_ft = self.height * unit_conversions[("cm", "ft")]
        # Convert the decimal part to inches
        remaining_height = (height_in_ft % 10) * unit_conversions[("ft", "in")]
        return [round(height_in_ft), round(remaining_height)]

    # The equation for bmi is weight/(height^2) in kg and meters
    def get_bmi(self):
        return self.weight / pow((self.height * unit_conversions[("cm", "m")]), 2)

# Food class has data about the amount of calories, macronutrients, and nutrients.
class Food(models.Model):
    pass


# A collection of Food
class Recipe(models.Model):
    pass


# DailyEntry contains information about your total calories intake for the day, exercised, etc.
class DailyEntry(models.Model):
    pass
