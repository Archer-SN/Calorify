from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser
from math import floor
from datetime import datetime

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

PROTEIN_ID = 1003
TOTAL_LIPIDS_ID = 1004
CARBS_ID = 1005


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
    weight = models.IntegerField(default=60)
    # Store height in cm
    height = models.IntegerField(default=170)
    body_fat = models.FloatField(default=15)
    year_born = models.DateField(default=datetime.now)

    activity_level = models.FloatField(choices=ActivityLevel.choices, default=ActivityLevel.SEDENTARY)

    # TODO : Macronutrients target for protein, carbs, and fats.

    def __str__(self):
        return self.username

    # TODO
    def age(self):
        pass

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


# Nutrient is made as a model because there are hundreds of nutrients
class Nutrient(models.Model):
    name = models.CharField(max_length=64)
    # The standard unit of measure for the nutrient (per 100g of food)
    unit_name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


# The category of food
class FoodCategory(models.Model):
    # The name of the category
    description = models.CharField(max_length=64)
    # Food group code
    code = models.IntegerField()


# Food class has data about the amount of calories, macronutrients, and nutrients.
class Food(models.Model):
    # An id of the food in FDC database
    fdc_id = models.BigAutoField(primary_key=True)
    # Description of the food (i.e. its name)
    description = models.CharField(max_length=64)
    food_category = models.ManyToManyField(FoodCategory)
    note = models.TextField()

    def __str__(self):
        return self.description

    # Returns a dictionary of calorie factors for fat, protein, and carbs
    def get_calorie_factors(self):
        return self.food_nutrient_converter.food_calorie_converter.calorie_factorts()


# Top level type for all types of nutrient converter.
# There are 3 types: fat, protein, carbohydrates
# Nutrient converter converts micronutrients to macronutrients
class FoodNutrientConversionFactor(models.Model):
    food = models.OneToOneField(Food, blank=True, null=True, related_name="food_nutrient_converter",
                                on_delete=models.CASCADE)


class FoodFatConversionFactor(models.Model):
    food_nutrient_cf = models.OneToOneField(FoodNutrientConversionFactor, blank=True, null=True,
                                            related_name="food_fat_converter",
                                            on_delete=models.CASCADE)
    value = models.FloatField(null=True, )


class FoodProteinConversionFactor(models.Model):
    food_nutrient_cf = models.OneToOneField(FoodNutrientConversionFactor, blank=True, null=True,
                                            related_name="food_protein_converter",
                                            on_delete=models.CASCADE)
    value = models.FloatField(null=True, )


# This contains the multiplication factors that will be used
# when calculating energy from macronutrients for a specific food
class FoodCalorieConversionFactor(models.Model):
    food_nutrient_cf = models.OneToOneField(FoodNutrientConversionFactor,
                                            blank=True,
                                            null=True,
                                            related_name="food_calorie_converter",
                                            on_delete=models.CASCADE)
    # The multiplication factors for each macronutrient
    fat_value = models.FloatField(null=True)
    protein_value = models.FloatField(null=True)
    carbohydrate_value = models.FloatField(null=True)

    # Returns a dictionary of calorie factors for fat, protein, and carbs
    def calorie_factors(self):
        factors = {"fats": self.fat_value, "protein": self.protein_value, "carbohydrates": self.carbohydrate_value}
        return factors


# MeasureUnit will store all the names of all the units
class MeasureUnit(models.Model):
    unit_name = models.CharField(max_length=32)


# A nutrient value for each food
class FoodNutrient(models.Model):
    food = models.ForeignKey(Food, blank=True, related_name="food_nutrient", on_delete=models.CASCADE)
    # The nutrient of which the food nutrient pertains
    nutrient = models.ManyToManyField(Nutrient, related_name="food_nutrient")
    # The amount of the nutrient in food per 100g
    amount = models.FloatField()


# This model store the default portion of each food
class FoodPortion(models.Model):
    # The food that this portion relates to
    food = models.ForeignKey(Food, blank=True, related_name="food_portion", on_delete=models.CASCADE)
    measure_unit = models.ForeignKey(MeasureUnit, default=None, null=True, blank=True,related_name="food_portion", on_delete=models.CASCADE)
    # Amount of the food
    amount = models.FloatField()
    portion_description = models.CharField(max_length=64)
    # Weight of the food portion in gram
    gram_weight = models.FloatField()


# A collection of Food
class Recipe(models.Model):
    name = models.CharField(max_length=64)
    foods = models.ManyToManyField(Food, blank=False)
    note = models.TextField()


# DailyEntry contains information about your total calories intake for the day, exercised, etc.
class DailyEntry(models.Model):
    date = models.DateField(default=datetime.now)

    # TODO: Track Macronutrients
    # TODO: Return the total calories consumed
    def total_calories(self):
        total = 0
        for user_food in UserFood.objects.filter(daily_entry=self):
            total += user_food.get_calories()
        return total


# Food entry created by the user
class UserFood(models.Model):
    food = models.ForeignKey(Food, related_name="user_food", on_delete=models.CASCADE)
    # The daily entry this food belongs to
    daily_entry = models.ForeignKey(DailyEntry, related_name="user_food", on_delete=models.CASCADE)
    # Food amount in grams
    amount = models.FloatField()

    # Return the total amount of protein in grams
    def get_protein(self):
        return self.food.food_nutrient.objects.get(id=PROTEIN_ID).amount

    # Return the total amount of carbs in grams
    def get_carbs(self):
        return self.food.food_nutrient.objects.get(id=CARBS_ID).amount

    # Return the total amount of fat in grams
    def get_fats(self):
        return self.food.food_nutrient.objects.get(id=TOTAL_LIPIDS_ID).amount

    # Return the total calories from all macronutrients
    def get_calories(self):
        cf = self.food.get_calorie_factors()
        return (cf["protein"] * self.get_protein()) + (cf["carbohydrates"] * self.get_carbs()) + (
                    cf["fats"] * self.get_fats())
