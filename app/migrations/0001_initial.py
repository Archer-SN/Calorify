# Generated by Django 4.2.3 on 2023-07-22 16:33

import app.fields
import app.models
import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('sex', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=1)),
                ('weight', models.FloatField(default=75)),
                ('height', models.IntegerField(default=175)),
                ('body_fat', models.FloatField(default=15)),
                ('date_born', models.DateField(default=datetime.datetime.now)),
                ('activity_level', models.CharField(choices=[('NONE', 'None'), ('SED', 'Sedentary'), ('LA', 'Lightly Active'), ('MA', 'Moderately Active'), ('VA', 'Very Active')], default='NONE', max_length=4)),
                ('meal_frequency', models.IntegerField(default=3, validators=[django.core.validators.MaxValueValidator(10)])),
                ('recommendation_frequency', models.IntegerField(default=30, validators=[django.core.validators.MinValueValidator(30.0)])),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='DailyEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_entries', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Difficulty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('xp', models.PositiveIntegerField()),
                ('gems', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('food_id', models.CharField(max_length=128, primary_key=True, serialize=False, unique=True)),
                ('label', models.CharField(max_length=64)),
                ('note', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='FoodCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='MeasureUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.CharField(max_length=128)),
                ('unit_name', models.CharField(max_length=32, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Nutrient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ntr_code', models.CharField(max_length=32)),
                ('label', models.CharField(max_length=64)),
                ('unit_name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='UserTargets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight_goal', models.FloatField(default=0)),
                ('weight_goal_rate', models.IntegerField(default=0)),
                ('protein_target', models.FloatField(default=25)),
                ('carbs_target', models.FloatField(default=45)),
                ('fat_target', models.FloatField(default=30)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserRPG',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', app.fields.IntegerRangeField(default=1)),
                ('max_xp', models.PositiveIntegerField(default=0)),
                ('current_xp', models.PositiveIntegerField(default=0)),
                ('gems', models.PositiveIntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFood',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField(default=0)),
                ('time_added', models.TimeField(default=datetime.time(0, 0))),
                ('daily_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_foods', to='app.dailyentry')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_foods', to='app.food')),
            ],
        ),
        migrations.CreateModel(
            name='UserExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.IntegerField(default=0)),
                ('time_added', models.TimeField(default=datetime.time(0, 0))),
                ('daily_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_exercises', to='app.dailyentry')),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_exercises', to='app.exercise')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('note', models.TextField()),
                ('foods', models.ManyToManyField(to='app.food')),
            ],
        ),
        migrations.CreateModel(
            name='FoodPortion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0)),
                ('portion_description', models.CharField(max_length=64)),
                ('gram_weight', models.FloatField()),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_portions', to='app.food')),
                ('measure_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_portions', to='app.measureunit')),
            ],
        ),
        migrations.CreateModel(
            name='FoodNutrient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_nutrients', to='app.food')),
                ('nutrient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_nutrients', to='app.nutrient')),
            ],
        ),
        migrations.AddField(
            model_name='food',
            name='food_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.foodcategory'),
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('is_completed', models.BooleanField(default=False)),
                ('date_created', models.DateField(default=datetime.datetime.now)),
                ('expire_date', models.DateField(default=app.models.tomorrow)),
                ('difficulty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.difficulty')),
                ('user', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
