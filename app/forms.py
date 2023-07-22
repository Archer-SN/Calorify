from django import forms
from datetime import time, datetime, date
import os
import django

# Units are hard coded for now
UNIT_CHOICES = (
    ("http://www.edamam.com/ontologies/edamam.owl#Measure_gram", "g"),
    ("http://www.edamam.com/ontologies/edamam.owl#Measure_ounce", "oz"),
)


class UserForm(forms.Form):
    ACTIVITY_LEVEL = [
        ("NONE", "None"),
        ("SED", "Sedentary"),
        ("LA", "Lightly Active"),
        ("MA", "Moderately Active"),
        ("VA", "Very Active"),
    ]

    SEX_CHOICES = [("M", "Male"), ("F", "Female")]
    date_born = forms.DateField(
        label="Date of Birth (Year/Month/Day)", initial=date(2000, 1, 1)
    )
    sex = forms.ChoiceField(label="Biological Sex", choices=SEX_CHOICES)
    height = forms.IntegerField(label="Height (cm)", initial=170)
    weight = forms.FloatField(label="Weight (kg)", initial=70)
    body_fat = forms.FloatField(label="Body Fat Percentage(Optional)", initial=15)
    activity_level = forms.ChoiceField(label="Activity Level", choices=ACTIVITY_LEVEL)
    meal_frequency = forms.IntegerField(
        label="How many meals do you eat per day?", initial=3
    )
    recommendation_frequency = forms.IntegerField(
        label="How often do you want ChatGPT to recommend you? (In days)", initial=30
    )
    weight_goal = forms.FloatField(label="What's your weight goal?")
    weight_goal_rate = forms.FloatField(label="How much deficit/surplus?")
    csrfmiddlewaretoken = forms.CharField(
        max_length=100, widget=forms.HiddenInput(), required=False
    )


# Forms
class UserFoodForm(forms.Form):
    # csrfmiddlewaretoken = forms.CharField(
    #     max_length=100, widget=forms.HiddenInput(), required=False
    # )
    food_id = forms.CharField(
        max_length=100, widget=forms.HiddenInput(), required=False
    )
    daily_entry_date = forms.DateField(widget=forms.HiddenInput(), required=False)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    time_added = forms.TimeField(
        label="Time of Day",
        initial=time(int(now.strftime("%H")), int(now.strftime("%M"))),
        widget=forms.TimeInput(format="%H:%M"),
    )
    amount = forms.FloatField(initial=1)
    # TODO: Unit Feature omitted for now
    unit = forms.ChoiceField(choices=UNIT_CHOICES)
