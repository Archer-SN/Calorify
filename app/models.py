from django.core.validators import MinValueValidator, MaxValueValidator
from model_utils import Choices

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
UNIT_CHOICES = (
    ("cm", "centimeters"),
    ("kg", "kilograms"),
    ("in", "inches"),
    ("ft", "feet"),
    ("lbs", "pounds"),
)

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

ACTIVITY_LEVEL_MULTIPLIER = {
    "NONE": 1,
    "SED": 1.2,
    "LA": 1.35,
    "MA": 1.5,
    "VA": 1.9,
}

READABLE_ACTIVITY_LEVEL = {
    "NONE": "None",
    "SED": "Sedentary",
    "LA": "Lightly Active",
    "MA": "Moderately Active",
    "VA": "Very Active",
}

READABLE_SEX = {"M": "Male", "F": "Female"}

# Create your models here.


# This model stores all the basic information of the user
class User(AbstractUser):
    # This will be multiplied to BMR which will give Total Daily Energy Expenditure (TDEE)
    ACTIVITY_LEVEL = Choices(
        ("NONE", _("None")),
        ("SED", _("Sedentary")),
        ("LA", _("Lightly Active")),
        ("MA", _("Moderately Active")),
        ("VA", _("Very Active")),
    )

    SEX_CHOICES = [("M", "Male"), ("F", "Female")]
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)

    # Store weight in kg
    weight = models.FloatField(default=60)
    # Store height in cm
    height = models.IntegerField(default=170)
    body_fat = models.FloatField(default=15)
    date_born = models.DateField(default=datetime.now)

    activity_level = models.CharField(
        max_length=4, choices=ACTIVITY_LEVEL, default=ACTIVITY_LEVEL.NONE
    )

    meal_frequency = models.IntegerField(default=3, validators=[MaxValueValidator(10)])

    # The interval between the AI meal plan and routine recommendation
    # We store it in days
    recommendation_frequency = models.IntegerField(
        default=30, validators=[MinValueValidator(30.0)]
    )

    field_history = FieldHistoryTracker(["weight", "body_fat", "activity_level"])

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        if created:
            UserRPG.objects.create(user=self)
            UserTargets.objects.create(user=self)

    def age(self):
        return int(datetime.now().year - self.date_born.year)

    def get_activity_level_multiplier(self):
        return ACTIVITY_LEVEL_MULTIPLIER[self.activity_level]

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
            return float(
                10 * (self.weight) + (6.25 * self.height) - 5 * (self.age()) + 5
            )
        else:
            return 10 * (self.weight) + (6.25 * self.height) - 5 * (self.age()) - 161

    # Return TDEE as a float
    def get_tdee(self):
        bmr = self.get_bmr()
        return bmr * self.get_activity_level_multiplier()

    # Total Dail Energy Goal (TDEE + weight goal rate [in calories])
    def get_tdeg(self):
        return self.get_tdee() + UserTargets.objects.get(user=self).weight_goal_rate

    # Calculate the change in weight since the specified date
    # Positive (negative) means weight gain (loss)
    def calculate_weight_change(self, date):
        pass

    def info(self):
        goal = UserTargets.objects.get(user=self).goal()
        return "Sex: {sex}, Height: {height} cm, Age: {age}, Weight: {weight} kg,Activity Level: {activity_level}, Meal Frequency: {meal_frequency}, Total Calories Goal: {tdeg}, Goal: {goal}".format(
            sex=READABLE_SEX[self.sex],
            height=self.height,
            weight=self.weight,
            age=self.age(),
            activity_level=READABLE_ACTIVITY_LEVEL[self.activity_level],
            meal_frequency=self.meal_frequency,
            tdeg=self.get_tdeg(),
            goal=goal,
        )


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

    def goal(self):
        weight_difference = self.weight_goal - self.user.weight
        user_goal = ""
        if weight_difference > 0:
            user_goal = "Gain weight"
        elif weight_difference < 0:
            user_goal = "Lose weight"
        else:
            user_goal = "Maintain weight"
        return user_goal


# This model handles the RPG system for the user
class UserRPG(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    level = fields.IntegerRangeField(default=1, min_value=1, max_value=99)
    max_xp = models.PositiveIntegerField(default=0)
    current_xp = models.PositiveIntegerField(default=0)
    gems = models.PositiveIntegerField(default=0)

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

    def gain_gems(self, gems_amount):
        self.gems += gems_amount


class Difficulty(models.Model):
    # Name of the difficulty
    name = models.CharField(max_length=64)
    # Description of the difficulty
    description = models.TextField()
    # How much xp will be gained upon completion
    xp = models.PositiveIntegerField()
    # How many gems will be rewarded
    gems = models.PositiveIntegerField()


class Challenge(models.Model):
    user_rpg = models.ManyToManyField(UserRPG)
    difficulty = models.ForeignKey(Difficulty, on_delete=models.CASCADE)
    # The challenge's name
    name = models.CharField(max_length=64)
    # The description of the challenge
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    date_created = models.DateField(default=datetime.now)
    expire_date = models.DateField(default=datetime.now)

    def complete_challenge(self):
        self.is_completed = True
        self.user_rpg.gain_xp(self.difficulty.xp)
        self.user_rpg.gain_gems(self.difficulty.gems)

    def is_expired(self):
        if datetime.now() > self.expire_date:
            return True
        return False


class Nutrient(models.Model):
    # The code that the food database uses for identifying the nutrient
    ntr_code = models.CharField(max_length=32)
    # The name of the nutrient
    label = models.CharField(max_length=64)
    # The standard unit of measure for the nutrient (per 100g of food)
    unit_name = models.CharField(max_length=32)

    def __str__(self):
        return self.label


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

    # Return the amount of each nutrient in the food based on the given food weight
    def get_all_nutrients(self, weight=BASE_AMOUNT):
        nutrients_counter = Counter()
        for food_nutrient in FoodNutrient.objects.filter(food=self).select_related(
            "nutrient"
        ):
            ntr_code = food_nutrient.nutrient.ntr_code
            nutrients_counter[ntr_code] = (food_nutrient.amount / BASE_AMOUNT) * weight
        return nutrients_counter

    # Return the amount of the nutrient in the food based on the given food weight
    def get_nutrient(self, nutrient_code, weight=BASE_AMOUNT):
        nutrient = Nutrient.objects.get(ntr_code=nutrient_code)
        # TODO: Fix this
        food_nutrient = FoodNutrient.objects.filter(food=self, nutrient=nutrient)[0]
        amount = (food_nutrient.amount / BASE_AMOUNT) * weight
        return amount


# MeasureUnit will store all the names of all the units
class MeasureUnit(models.Model):
    uri = models.CharField(max_length=128)
    unit_name = models.CharField(max_length=32, unique=True)


# A nutrient value for each food
class FoodNutrient(models.Model):
    food = models.ForeignKey(
        Food, related_name="food_nutrients", on_delete=models.CASCADE
    )
    # The nutrient of which the food nutrient pertains
    nutrient = models.ForeignKey(
        Nutrient, related_name="food_nutrients", on_delete=models.CASCADE
    )
    # The amount of the nutrient in food per 100g
    amount = models.FloatField()


# This model store the default portion of each food
class FoodPortion(models.Model):
    # The food that this portion relates to
    food = models.ForeignKey(
        Food, related_name="food_portions", on_delete=models.CASCADE
    )
    measure_unit = models.ForeignKey(
        MeasureUnit, related_name="food_portions", on_delete=models.CASCADE
    )
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
    user = models.ForeignKey(
        User, related_name="daily_entries", on_delete=models.CASCADE
    )
    date = models.DateField(default=datetime.now)

    # This summary will be used by AI
    # A shortened version of summary to reduce API usage cost
    def ai_summarize(self):
        food_intake = []
        exercises = []
        nutrients = self.total_nutrients()
        for user_food in UserFood.objects.filter(daily_entry=self):
            food_intake.append(user_food.info())
        for exercise in UserExercise.objects.filter(daily_entry=self):
            exercises.append(exercise.info())

        return {
            "d": self.date,
            "i": food_intake,
            "e": exercises,
            "k": nutrients["ENERC_KCAL"],
            "m": {
                "p": nutrients["PROCNT"],
                "c": nutrients["CHOCDF.net"],
                "f": nutrients["FAT"],
            },
        }

    # A more detailed version of Daily Entry summary
    # It is used in html templates
    def summarize(self):
        food_intake = []
        exercises = []
        nutrients = self.total_nutrients()
        for user_food in UserFood.objects.filter(daily_entry=self):
            food_intake.append(user_food.data())
        for exercise in UserExercise.objects.filter(daily_entry=self):
            exercises.append(exercise.data())

        return {
            "date": self.date,
            "food_intake": food_intake,
            "exercises": exercises,
            "nutrients": {
                "general": {
                    "energy": nutrients.get("ENERC_KCAL", 0),
                    "water": nutrients.get("WATER", 0),
                },
                "carbohydrates": {
                    "carbs": nutrients.get("CHOCDF.net", 0),
                    "sugar": nutrients.get("SUGAR", 0),
                    "fiber": nutrients.get("FIBTG", 0),
                },
                "lipids": {
                    "fat": nutrients.get("FAT", 0),
                    "monosaturated": nutrients.get("FAMS", 0),
                    "polyunsaturated": nutrients.get("FAPU", 0),
                    "saturated": nutrients.get("FASAT", 0),
                    "trans-fats": nutrients.get("FATRN", 0),
                    "cholesterol": nutrients.get("CHOLE", 0),
                },
                "protien": {
                    "protein": nutrients.get("PROCNT", 0),
                },
                "vitamins": {
                    "b1": nutrients.get("THIA", 0),
                    "b2": nutrients.get("RIBF", 0),
                    "b3": nutrients.get("NIA", 0),
                    "b6": nutrients.get("VITB6A", 0),
                    "b12": nutrients.get("VITB12", 0),
                    "folate": nutrients.get("FOLFD", 0),
                    "vitamin a": nutrients.get("VITA_RAE", 0),
                    "vitamin c": nutrients.get("VITC", 0),
                    "vitamin d": nutrients.get("VITD", 0),
                    "vitamin e": nutrients.get("TOCPHA", 0),
                    "vitamin k": nutrients.get("VITK1", 0),
                },
                "minerals": {
                    "calcium": nutrients.get("CA", 0),
                    "iron": nutrients.get("FE", 0),
                    "magnesium": nutrients.get("MG", 0),
                    "phosphorus": nutrients.get("P", 0),
                    "potassium": nutrients.get("K", 0),
                    "sodium": nutrients.get("NA", 0),
                    "zinc": nutrients.get("ZN", 0),
                },
            },
        }

    # Returns the total nutrients consumed for the day
    def total_nutrients(self):
        total_nutrients_counter = Counter()
        for user_food in UserFood.objects.filter(daily_entry=self):
            total_nutrients_counter += user_food.get_all_nutrients()
        return dict(total_nutrients_counter)


# Food entry created by the user
class UserFood(models.Model):
    food = models.ForeignKey(Food, related_name="user_foods", on_delete=models.CASCADE)
    # The daily entry this food belongs to
    daily_entry = models.ForeignKey(
        DailyEntry, related_name="user_foods", on_delete=models.CASCADE
    )
    # Food weight in grams
    weight = models.FloatField(default=0)

    # Returns basic information of the user food. In this case, the name.
    def info(self):
        return {"l": self.food.label}

    # Returns detailed information of the user food.
    # It is used in html
    def data(self):
        return {
            "id": self.id,
            "name": self.food.label,
            "weight": self.weight,
            "energy": self.get_nutrient("ENERC_KCAL"),
        }

    # Return the amount of each nutrient in the food
    def get_all_nutrients(self):
        return self.food.get_all_nutrients(self.weight)

    def get_nutrient(self, nutrient_code):
        return self.food.get_nutrient(nutrient_code, self.weight)


# Stores the name and description of each exercise.
class Exercise(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()


# Exercise entry created by the user
class UserExercise(models.Model):
    exercise = models.ForeignKey(
        Exercise, related_name="user_exercises", on_delete=models.CASCADE
    )
    daily_entry = models.ForeignKey(
        DailyEntry, related_name="user_exercises", on_delete=models.CASCADE
    )
    duration = models.IntegerField(default=0)

    # Returns basic information of the exercise.
    def info(self):
        return {"n": self.exercise.name, "t": self.duration}

    # Returns detailed information of the user exercise.
    # It is used in html
    def data(self):
        return {
            "id": self.id,
            "name": self.exercise.name,
            "duration": self.duration,
        }
