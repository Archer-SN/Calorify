# Generated by Django 4.0.4 on 2023-07-01 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_foodcalorieconversionfactor_food_nutrient_cf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodcalorieconversionfactor',
            name='food_nutrient_cf',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='food_calorie_converter', to='app.foodnutrientconversionfactor'),
        ),
    ]
