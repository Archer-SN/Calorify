from django.core.validators import MinValueValidator

from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser
from math import floor
from datetime import datetime
from field_history.tracker import FieldHistoryTracker
from collections import Counter

from . import fields

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

# The calories, protein, carbs, fat, etc. intake will be based on this amount
# This is like "per 100g"
BASE_AMOUNT = 100


# Create your models here.


# This model stores all the basic information of the user
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
    weight = models.FloatField(default=60)
    # Store height in cm
    height = models.IntegerField(default=170)
    body_fat = models.FloatField(default=15)
    year_born = models.DateField(default=datetime.now)

    activity_level = models.FloatField(choices=ActivityLevel.choices, default=ActivityLevel.SEDENTARY)

    # The interval between the AI meal plan and routine recommendation
    # We store it in days
    recommendation_frequency = models.IntegerField(default=30, validators=[MinValueValidator(30.0)])

    field_history = FieldHistoryTracker(["weight", "body_fat", "activity_level"])

    def __str__(self):
        return self.username

    def age(self):
        return datetime.now().year - self.year_born.year

    def to_lbs(self):
        return round(self.weight * unit_conversions[("kg", "lbs")])

    # Convert the user height from cm to f
    def to_ft_in(self):
        # Convert height from centimeters to feet
        height_in_ft = self.height * unit_conversions[("cm", "ft")]
        # Convert the decimal part to inches
        remaining_height = (height_in_ft % 10) * unit_conversions[("ft", "in")]
        return [floor(height_in_ft), round(remaining_height)]

    # The equation for bmi is weight/(height^2) in kg and meters
    def get_bmi(self):
        return self.weight / pow((self.height * unit_conversions[("cm", "m")]), 2)

    # Calculate basal metabolic rate
    def get_bmr(self):
        if self.sex == "M":
            return (10 * self.weight) + (6.25 * self.height) - (5 * self.age()) + 5
        else:
            return (10 * self.weight) + (6.25 * self.height) - (5 * self.age()) - 161

    # Return TDEE as a float
    def get_tdee(self):
        bmr = self.get_bmr()
        return bmr + (bmr * self.activity_level)


# This model handles user's target for macronutrients, weight, etc.
class UserTargets(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    weight_goal = models.FloatField(default=0)

    # The rate of surplus or deficit
    weight_goal_rate = models.IntegerField(default=0)

    # These are macro ratios
    protein_target = models.FloatField(default=25)
    carbs_target = models.FloatField(default=45)
    fat_target = models.FloatField(default=30)


# This model handles the level system for the user
class UserLevel(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    level = fields.IntegerRangeField(default=1, min_value=1, max_value=99)
    max_xp = models.PositiveIntegerField(default=0)
    current_xp = models.PositiveIntegerField(default=0)

    def calculate_xp(self):
        x = 0.3
        y = 2
        return pow((self.level / x), y)

    def level_up(self):
        if self.current_xp >= self.max_xp:
            # Level up
            self.level += 1
            # Deduct the current xp with the max xp
            self.current_xp -= self.max_xp
            # Calculate new max xp
            self.max_xp = self.calculate_xp()

    def gain_xp(self, xp_amount):
        self.current_xp += xp_amount
        # In case the current xp exceeds the max xp
        self.level_up()


class Challenge:
    user = models.ManyToManyField(User)
    # An xp that the user will gain for completing th challenge
    xp = models.PositiveIntegerField(default=0)
    # The challenge's name
    name = models.CharField(max_length=64)
    # The description of the challenge
    description = models.TextField()
    is_completed = models.BooleanField(default=False)

    def complete_challenge(self):
        self.is_completed = True
        self.user.gain_xp(self.xp)


class Nutrient(models.Model):
    # The code that the food database uses for identifying the nutrient
    ntr_code = models.CharField(max_length=32)
    name = models.CharField(max_length=64)
    # The standard unit of measure for the nutrient (per 100g of food)
    unit_name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


# The category of food
class FoodCategory(models.Model):
    # The name of the category
    description = models.CharField(max_length=64)


# Food class has data about the amount of calories, macronutrients, and nutrients.
class Food(models.Model):
    # An id of the food in EDAMAM database
    food_id = models.CharField(max_length=128, unique=True, primary_key=True)
    # Label of the food (i.e. its name)
    label = models.CharField(max_length=64)
    food_category = models.ForeignKey(FoodCategory, null=True, on_delete=models.CASCADE)
    note = models.TextField()

    def __str__(self):
        return self.label


# MeasureUnit will store all the names of all the units
class MeasureUnit(models.Model):
    uri = models.CharField(max_length=128)
    unit_name = models.CharField(max_length=32, unique=True)


# A nutrient value for each food
class FoodNutrient(models.Model):
    food = models.ForeignKey(Food, related_name="food_nutrients", on_delete=models.CASCADE)
    # The nutrient of which the food nutrient pertains
    nutrient = models.ForeignKey(Nutrient, related_name="food_nutrients", on_delete=models.CASCADE)
    # The amount of the nutrient in food per 100g
    amount = models.FloatField()


# This model store the default portion of each food
class FoodPortion(models.Model):
    # The food that this portion relates to
    food = models.ForeignKey(Food, related_name="food_portions", on_delete=models.CASCADE)
    measure_unit = models.ForeignKey(MeasureUnit, related_name="food_portions",
                                     on_delete=models.CASCADE)
    # Amount of the food
    amount = models.FloatField(default=0)
    portion_description = models.CharField(max_length=64)
    # Weight of the food portion in gram
    gram_weight = models.FloatField()


# A collection of Food
# TODO
class Recipe(models.Model):
    name = models.CharField(max_length=64)
    foods = models.ManyToManyField(Food, blank=False)
    note = models.TextField()


# DailyEntry contains information about your total calories intake for the day, exercised, etc.
class DailyEntry(models.Model):
    user = models.ForeignKey(User, related_name="daily_entries", on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now, unique=True)

    def total_nutrients(self):
        total_nutrients_counter = Counter()
        for user_food in UserFood.objects.filter(daily_entry=self):
            total_nutrients_counter += user_food.get_nutrients()
        return total_nutrients_counter

    def total_calories(self):
        return self.total_nutrients()["ENERC_KCAL"]


# Food entry created by the user
class UserFood(models.Model):
    food = models.ForeignKey(Food, related_name="user_foods", on_delete=models.CASCADE)
    # The daily entry this food belongs to
    daily_entry = models.ForeignKey(DailyEntry, related_name="user_foods", on_delete=models.CASCADE)
    # Food weight in grams
    weight = models.FloatField(default=0)

    def __str__(self):
        return self.food.label

    # Return the amount of each nutrient in the food
    def get_nutrients(self):
        nutrients_counter = Counter()
        for food_nutrient in self.food.food_nutrients.all():
            nutrient_name = food_nutrient.nutrient.name
            nutrients_counter[nutrient_name] = (food_nutrient.amount / BASE_AMOUNT) * self.amount
        return nutrients_counter
