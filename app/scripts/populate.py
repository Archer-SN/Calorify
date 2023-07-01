import os, django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calorify.settings")
django.setup()

from app.models import *

FDC_DATA_PATH = "../../../FDC_data/"

# TODO: MAKE THIS SCRIPT FASTER!!!!!!!!!!!!!

# CF stands for conversion factor

NUTRIENT_PATH = FDC_DATA_PATH + "nutrient.csv"
FOOD_PATH = FDC_DATA_PATH + "food.csv"
FOOD_NUTRIENT_CF_PATH = FDC_DATA_PATH + "food_nutrient_conversion_factor.csv"
FOOD_FAT_CF_PATH = FDC_DATA_PATH + "foot_fat_conversion_factor.csv"
FOOD_PROTEIN_CF_PATH = FDC_DATA_PATH + "food_protein_conversion_factor.csv"
FOOD_CALORIE_CF_PATH = FDC_DATA_PATH + "food_calorie_conversion_factor.csv"
MEASURE_UNIT_PATH = FDC_DATA_PATH + "measure_unit.csv"
FOOD_NUTRIENT_PATH = FDC_DATA_PATH + "food_nutrient.csv"
FOOD_PORTION_PATH = FDC_DATA_PATH + "food_portion.csv"
FOOD_CATEGORY_PATH = FDC_DATA_PATH + "food_category.csv"


# DON'T FORGET TO SKIP THE FIRST ROW OF THE TABLE!
# THE FIRST ROW CONTAINS A HEADER WHICH WILL CAUSE AN ERROR!

# Populate Nutrient models
def nutrient():
    with open(NUTRIENT_PATH) as f:
        reader = csv.reader(f)
        objs = []
        for row in reader:
            if row[0] != "id":
                objs.append(Nutrient(id=row[0], name=row[1], unit_name=row[2]))
        Nutrient.objects.bulk_create(objs)

    print("Nutrient Done!")


# Populate FoodCategory models
def food_category():
    with open(FOOD_CATEGORY_PATH) as f:
        reader = csv.reader(f)
        objs = []
        for row in reader:
            if row[0] != "id":
                objs.append(FoodCategory(id=row[1], description=row[2]))
        FoodCategory.objects.bulk_create(objs)
    print("FoodCategory Done!")


def food():
    # Populate Food models
    with open(FOOD_PATH, encoding="utf8") as f:
        reader = csv.reader(f)
        objs = []
        for row in reader:
            if row[0] != "fdc_id":
                try:
                    #TODO: Omit food category for now
                    objs.append(Food(fdc_id=row[0], description=row[2]))
                except FoodCategory.DoesNotExist:
                    pass
        Food.objects.bulk_create(objs)
    print("Food Done!")


def food_nutrient_cf():
    # Populate FoodNutrientConversionFactor models
    with open(FOOD_NUTRIENT_CF_PATH) as f:
        reader = csv.reader(f)
        objs = []
        for row in reader:
            if row[0] != "id":
                try:
                    objs.append(FoodNutrientConversionFactor(id=row[0], food_id=row[1]))
                except Food.DoesNotExist:
                    pass
        FoodNutrientConversionFactor.objects.bulk_create(objs)
    print("FoodNutrientConversionFactor Done!")


# Populate FoodFatConversionFactor models
# Not sure whether this file exists (It is not in FDC_data folder)
def food_fat_cf():
    with open(FOOD_FAT_CF_PATH) as f:
        reader = csv.reader(f)
        objs = []
        for row in reader:
            if row[0] != "id":
                pass


# Populate FoodProteinConversionFactor models
def food_protein_cf():
    with open(FOOD_PROTEIN_CF_PATH) as f:
        reader = csv.reader(f)
        objs = []
        for row in reader:
            if row[0] != "food_nutrient_conversion_factor_id":
                try:
                    objs.append(FoodProteinConversionFactor(
                        food_nutrient_cf_id=row[0], value=row[1]))
                except FoodNutrientConversionFactor.DoesNotExist:
                    pass
        FoodProteinConversionFactor.objects.bulk_create(objs)
    print("FoodProteinConversionFactor Done!")


# Populate FoodCalorieConversionFactor models
def food_calorie_cf():
    with open(FOOD_CALORIE_CF_PATH) as f:
        reader = csv.reader(f)
        objs = []
        for row in reader:
            if row[0] != "food_nutrient_conversion_factor_id":
                try:
                    protein_value = 0
                    fat_value = 0
                    carb_value = 0
                    if row[1].isnumeric():
                        protein_value = row[1]
                    if row[2].isnumeric():
                        fat_value = row[2]
                    if row[3].isnumeric():
                        carb_value = row[3]
                    objs.append(FoodCalorieConversionFactor(
                        food_nutrient_cf_id=row[0], protein_value=protein_value,
                        fat_value=fat_value,
                        carbohydrate_value=carb_value))
                except FoodNutrientConversionFactor.DoesNotExist:
                    pass
        FoodCalorieConversionFactor.objects.bulk_create(objs)
    print("FoodCalorieConversionFactor Done!")


# Populate MeasureUnit models
def measure_unit():
    with open(MEASURE_UNIT_PATH) as f:
        reader = csv.reader(f)
        objs = []
        for row in reader:
            if row[0] != "id":
                objs.append(MeasureUnit(id=row[0], unit_name=row[1]))
        MeasureUnit.objects.bulk_create(objs)
    print("MeasureUnit Done!")


# Populate FoodPortion models
def food_portion():
    with open(FOOD_PORTION_PATH) as f:
        reader = csv.reader(f)
        objs = []
        for row in reader:
            if row[0] != "id":
                try:
                    amount = 0
                    if row[3].isnumeric():
                        amount = row[3]
                    objs.append(FoodPortion(id=row[0], food_id=row[1], amount=amount,
                                            measure_unit_id=row[4],
                                            portion_description=row[5],
                                            gram_weight=row[7]))
                except Food.DoesNotExist:
                    pass
                except FoodPortion.DoesNotExist:
                    pass
        FoodPortion.objects.bulk_create(objs)
    print("FoodPortion Done!")


# Populate FoodNutrient models
def food_nutrient():
    with open(FOOD_NUTRIENT_PATH) as f:
        reader = csv.reader(f)
        objs = []
        for row in reader:
            if row[0] != "id":
                try:
                    objs.append(FoodNutrient(id=row[0], amount=row[3],
                                             food_id=row[1], nutrient_id=row[2]))
                except Food.DoesNotExist:
                    pass
                except Nutrient.DoesNotExist:
                    pass
        FoodNutrient.objects.bulk_create(objs)

    print("FoodNutrient Done!")


# nutrient()
# food_category()
# food()
# measure_unit()
# food_portion()
# food_nutrient_cf()
# food_calorie_cf()
food_protein_cf()
food_nutrient()
