# Generated by Django 4.0.4 on 2023-07-07 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userfood',
            old_name='amount',
            new_name='weight',
        ),
        migrations.AlterField(
            model_name='measureunit',
            name='unit_name',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
