# Generated by Django 4.0.4 on 2023-07-05 12:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_dailyentry_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='recommendation_frequency',
            field=models.IntegerField(default=30, validators=[django.core.validators.MinValueValidator(30.0)]),
        ),
    ]
