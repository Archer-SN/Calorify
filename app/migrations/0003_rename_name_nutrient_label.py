# Generated by Django 4.0.4 on 2023-07-07 12:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_amount_userfood_weight_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nutrient',
            old_name='name',
            new_name='label',
        ),
    ]
