# Generated by Django 4.2.3 on 2023-08-02 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_exercisecategory_exercisedifficulty_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strengthexercise',
            name='category',
            field=models.CharField(max_length=24),
        ),
        migrations.AlterField(
            model_name='strengthexercise',
            name='difficulty',
            field=models.CharField(max_length=24),
        ),
        migrations.DeleteModel(
            name='ExerciseCategory',
        ),
        migrations.DeleteModel(
            name='ExerciseDifficulty',
        ),
    ]
