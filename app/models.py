from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser

# Calories here means kcal

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
    ("lbs", "kg"): (1 / 2.205),
    ("in", "ft"): (1 / 12),
    ("ft", "in"): 12,
    ("cm", "m"): (1 / 100),
    ("m", "cm"): 100,
}


# Create your models here.

class User(AbstractUser):
    # This will be multiplied to BMR which will give Total Daily Energy Expenditure (TDEE)
    class ActivityLevel(models.TextChoices):
        NONE = 1, _("None")
        SEDENTARY = 1.2, _("Sedentary")
        LIGHT = 1.35, _("Lightly Active")
        MODERATE = 1.5, _("Moderately Active")
        VERY = 1.9, _("Very Active")

    SEX_CHOICES = [("M", "Male"), ("F", "Female")]
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)

    # Store weight in kg
    weight = models.IntegerField()
    # Store height in cm
    height = models.IntegerField()
    body_fat = models.FloatField()

    activity_level = models.FloatField(choices=ActivityLevel)

    # TODO : Macronutrients target for protein, carbs, and fats.

    def __str__(self):
        return self.username

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

    # Return calories as a float
    def get_calories(self):
        # TODO
        pass


# Nutrient is made as a model because there are hundreds of nutrients
class Nutrient(models.Model):
    name = models.CharField(max_length=64)
    # The standard unit of measure for the nutrient (per 100g of food)
    unit_name = models.CharField(max_length=32)


# MeasureUnit will store all the names of all the units
class MeasureUnit(models.Model):
    unit_name = models.CharField(max_length=32)


# This model store the portion of each food
class FoodPortion(models.Model):
    # An id of the food in FDC database
    fdc_id = models.IntegerField()
    measure_unit_id = models.IntegerField()

    amount = models.FloatField()


class FoodCategory(models.Model):
    # The name of the category
    description = models.CharField(max_length=64)
    # Food group code
    code = models.IntegerField()


# Food class has data about the amount of calories, macronutrients, and nutrients.
class Food(models.Model):
    # An id of the food in FDC database
    fdc_id = models.IntegerField()
    # Description of the food (i.e. its name)
    description = models.CharField(max_length=64)

    note = models.TextField()

    # Return calories as a float
    def get_calories(self):
        pass


# A collection of Food
class Recipe(models.Model):
    name = models.CharField(max_length=64)
    foods = models.ManyToManyField(Food, blank=False)
    note = models.TextField()


# DailyEntry contains information about your total calories intake for the day, exercised, etc.
class DailyEntry(models.Model):
    food = models.ManyToManyField(Food, blank=True)

    # TODO: Track Macronutrients
    # TODO: Return the total calories consumed
    def total_calories(self):
        pass
