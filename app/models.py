from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    pass

# Food class has data about the amount of calories, macronutrients, and nutrients.
class Food(models.Model):
    pass

# A collection of Food
class Recipe(models.Model):
    pass

# DailyEntry contains information about your total calories intake for the day, exercised, etc.
class DailyEntry(models.Model):
    pass
