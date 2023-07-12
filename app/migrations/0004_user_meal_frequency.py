# Generated by Django 4.0.4 on 2023-07-12 14:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_rename_name_nutrient_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='meal_frequency',
            field=models.IntegerField(default=3, validators=[django.core.validators.MaxValueValidator(10)]),
        ),
    ]
