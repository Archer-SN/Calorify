# Generated by Django 4.2.3 on 2023-07-31 06:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userfood',
            name='unit',
        ),
    ]
