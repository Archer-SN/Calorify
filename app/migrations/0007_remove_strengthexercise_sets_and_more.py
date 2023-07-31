# Generated by Django 4.2.3 on 2023-07-31 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_userstrengthexercise_delete_userexercise'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='strengthexercise',
            name='sets',
        ),
        migrations.RemoveField(
            model_name='userstrengthexercise',
            name='duration',
        ),
        migrations.AddField(
            model_name='userstrengthexercise',
            name='reps',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='userstrengthexercise',
            name='sets',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='userstrengthexercise',
            name='weights',
            field=models.SmallIntegerField(default=0),
        ),
    ]
