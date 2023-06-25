import os, django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calorify.settings")
django.setup()

from app.models import *

FDC_DATA_PATH = "../../../FDC_data/"

# CF stands for conversion factor

NUTRIENT_PATH = FDC_DATA_PATH + "nutrient.csv"
FOOD_PATH = FDC_DATA_PATH + "food.csv"
FOOD_NUTRIENT_CF_PATH = FDC_DATA_PATH + "food_nutrient_conversion_factor.csv"
FOOD_FAT_CF_PATH = FDC_DATA_PATH + "foot_fat_conversion_factor.csv"
FOOD_PROTEIN_CF_PATH = FDC_DATA_PATH + "food_protein_conversion_factor.csv"
FOOD_CALORIE_CF_PATH = FDC_DATA_PATH + "food_calories_conversion_factor.csv"
MEASURE_UNIT_PATH = FDC_DATA_PATH + "measure_unit_path.csv"
FOOD_NUTRIENT_PATH = FDC_DATA_PATH + "food_nutrient.csv"
FOOD_PORTION_PATH = FDC_DATA_PATH + "food_portion.csv"
FOOD_CATEGORY_PATH = FDC_DATA_PATH + "food_category.csv"


# DON'T FORGET TO SKIP THE FIRST ROW OF THE TABLE!
# THE FIRST ROW CONTAINS A HEADER WHICH WILL CAUSE AN ERROR!

# Populate Nutrient models
def nutrient():
    with open(NUTRIENT_PATH) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != "id":
                _, created = Nutrient.objects.get_or_create(id=row[0], name=row[1], unit_name=row[2])

    print("Nutrient Done!")


# Populate FoodCategory models
def food_category():
    with open(FOOD_CATEGORY_PATH) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != "id":
                _, created = FoodCategory.objects.get_or_create(id=row[0], code=row[1], description=row[2])
    print("FoodCategory Done!")


def food():
    # Populate Food models
    with open(FOOD_PATH) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != "fdc_id":
                food, created = Food.objects.get_or_create(fdc_id=row[0], description=row[2])
                # food.food_category.add(FoodCategory.objects.get(id=row[3]))

    print("Food Done!")


def food_nutrient_cf():
    # Populate FoodNutrientConversionFactor models
    with open(FOOD_NUTRIENT_CF_PATH) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != "id":
                try:
                    food = Food.objects.get(fdc_id=row[1])
                    food_nutrient_cf, created = FoodNutrientConversionFactor.objects.get_or_create(id=row[0], food=food)
                except Food.DoesNotExist:
                    food_nutrient_cf, created = FoodNutrientConversionFactor.objects.get_or_create(id=row[0])

    print("FoodNutrientConversionFactor Done!")


# Populate FoodFatConversionFactor models
# Not sure whether this file exists (It is not in FDC_data folder)
def food_fat_cf():
    with open(FOOD_FAT_CF_PATH) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != "id":
                pass


# Populate FoodProteinConversionFactor models
def food_protein_cf():
    with open(FOOD_PROTEIN_CF_PATH) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != "food_nutrient_conversion_factor_id":
                food_nutrient_cf = FoodNutrientConversionFactor.objects.get(id=row[0])
                food_protein_cf, created = FoodProteinConversionFactor.objects.get_or_create(
                    food_nutrient_cf=food_nutrient_cf, value=row[1])

    print("FoodProteinConversionFactor Done!")


# Populate FoodCalorieConversionFactor models
def food_calorie_cf():
    with open(FOOD_CALORIE_CF_PATH) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != "food_nutrient_conversion_factor_id":
                food_nutrient_cf = FoodNutrientConversionFactor.objects.get(id=row[0])
                food_calorie_cf, created = FoodCalorieConversionFactor.objects.get_or_create(
                    food_nutrient_cf=food_nutrient_cf, protein_value=row[1],
                    fat_value=row[2],
                    carbohydrate_value=row[3])

    print("FoodCalorieConversionFactor Done!")


# Populate MeasureUnit models
def measure_unit():
    with open(MEASURE_UNIT_PATH) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != "id":
                _, created = MeasureUnit.objects.get_or_create(id=row[0], unit_name=row[1])

    print("MeasureUnit Done!")

# Populate FoodPortion models
def food_portion():
    with open(FOOD_PORTION_PATH) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != "id":
                try:
                    food = Food.objects.get(fdc_id=row[1])
                    food_portion, created = FoodPortion.objects.get_or_create(id=row[0], food=food, amount=row[3],
                                                                              measure_unit_id=row[4],
                                                                              portion_description=row[5],
                                                                              gram_weight=row[7])
                except Food.DoesNotExist:
                    food_portion, created = FoodPortion.objects.get_or_create(id=row[0], amount=row[3],
                                                                              measure_unit_id=row[4],
                                                                              portion_description=row[5],
                                                                              gram_weight=row[7])

    print("FoodPortion Done!")

# Populate FoodNutrient models
def food_nutrient():
    with open(FOOD_NUTRIENT_PATH) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != "id":
                nutrient = Nutrient.objects.get(id=row[2])
                try:
                    food = Food.objects.get(fdc_id=row[1])
                    food_nutrient, created = FoodNutrient.objects.get_or_create(id=row[0], amount=row[3], nutrient=nutrient,
                                                                                food=food)
                except Food.DoesNotExist:
                    food_nutrient, created = FoodNutrient.objects.get_or_create(id=row[0], amount=row[3], nutrient=nutrient,
                                                                                )

    print("FoodNutrient Done!")


nutrient()
food_category()
food()
measure_unit()
food_portion()
food_nutrient()

# Buggy
# TODO: FIX BUG
food_nutrient()
food_calorie_cf()
food_protein_cf()
