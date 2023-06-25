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
with open(NUTRIENT_PATH) as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] != "id":
            _, created = Nutrient.objects.get_or_create(id=row[0], name=row[1], unit_name=row[2])

# Populate FoodCategory models
with open(FOOD_CATEGORY_PATH) as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] != "id":
            _, created = FoodCategory.objects.get_or_create(id=row[0], code=row[1], description=row[2])

# Populate Food models
with open(FOOD_PATH) as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] != "fdc_id":
            food, created = Food.objects.get_or_create(fdc_id=row[0], description=row[2])
            food.food_category.add(FoodCategory.objects.get(id=row[3]))

# Populate FoodNutrientConversionFactor models
with open(FOOD_NUTRIENT_CF_PATH) as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] != "id":
            food = Food.objects.get(fdc_id=row[1])
            food_nutrient_cf, created = FoodNutrientConversionFactor.objects.get_or_create(id=row[0], food=food)

# Populate FoodFatConversionFactor models
# Not sure whether this file exists (It is not in FDC_data folder)
''' with open(FOOD_FAT_CF_PATH) as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] != "id":
            _, created = '''

# Populate FoodProteinConversionFactor models
with open(FOOD_PROTEIN_CF_PATH) as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] != "food_nutrient_conversion_factor_id":
            food_nutrient_cf = FoodNutrientConversionFactor.objects.get(id=row[0])
            food_protein_cf, created = FoodProteinConversionFactor.objects.get_or_create(food_nutrient_cf=food_nutrient_cf,value=row[1])

# Populate FoodCalorieConversionFactor models
with open(FOOD_CALORIE_CF_PATH) as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] != "food_nutrient_conversion_factor_id":
            food_nutrient_cf = FoodNutrientConversionFactor.objects.get(id=row[0])
            food_calorie_cf, created = FoodCalorieConversionFactor.objects.get_or_create(
                food_nutrient_cf=food_nutrient_cf, protein_value=row[1],
                fat_value=row[2],
                carbohydrate_value=row[3])

# Populate MeasureUnit models
with open(MEASURE_UNIT_PATH) as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] != "id":
            _, created = MeasureUnit.objects.get_or_create(id=row[0], unit_name=row[1])

# Populate FoodPortion models
with open(FOOD_PORTION_PATH) as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] != "id":
            food = Food.objects.get(fdc_id=row[1])
            food_portion, created = FoodPortion.objects.get_or_create(id=row[0], food=food, amount=row[3],
                                                                      measure_unit_id=row[4],
                                                                      portion_description=row[5], gram_weight=row[7])

# Populate FoodNutrient models
with open(FOOD_NUTRIENT_PATH) as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] != "id":
            nutrient = Nutrient.objects.get(id=row[2])
            food = Food.objects.get(fdc_id=row[1])
            food_nutrient, created = FoodNutrient.objects.get_or_create(id=row[0], amount=row[3], nutrient=nutrient,
                                                                        food=food)
