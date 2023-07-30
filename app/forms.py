from django import forms
from datetime import time, datetime, date
import os
import django

# Units are hard coded for now
UNIT_CHOICES = (
    ("http://www.edamam.com/ontologies/edamam.owl#Measure_gram", "g"),
    ("http://www.edamam.com/ontologies/edamam.owl#Measure_ounce", "oz"),
)


class AccountForm(forms.Form):
    username = forms.CharField(label="Username", max_length=32)
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Password", max_length=32, widget=forms.PasswordInput
    )
    password_confirmation = forms.CharField(
        label="Password Confirmation", max_length=32, widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                }
            )
            self.fields[field]


class HealthInfoForm(forms.Form):
    ACTIVITY_LEVEL = [
        ("NONE", "None"),
        ("SED", "Sedentary"),
        ("LA", "Lightly Active"),
        ("MA", "Moderately Active"),
        ("VA", "Very Active"),
    ]

    SEX_CHOICES = [("M", "Male"), ("F", "Female")]
    date_born = forms.DateField(
        label="Date of Birth",
        initial=date(2000, 1, 1),
        widget=forms.widgets.DateInput(attrs={"type": "date"}),
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

    def __init__(self, *args, **kwargs):
        super(HealthInfoForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                }
            )
            self.fields[field]


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
        widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
    )
    amount = forms.FloatField(initial=100)
    # TODO: Unit Feature omitted for now
    unit = forms.ChoiceField(choices=UNIT_CHOICES)

    def __init__(self, *args, **kwargs):
        super(UserFoodForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                }
            )
            self.fields[field]
