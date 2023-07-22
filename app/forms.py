from django import forms
from datetime import time, datetime


# Units are hard coded for now
UNIT_CHOICES = (
    ("http://www.edamam.com/ontologies/edamam.owl#Measure_gram", "g"),
    ("http://www.edamam.com/ontologies/edamam.owl#Measure_ounce", "oz"),
)


# Forms
class UserFoodForm(forms.Form):
    food_id = forms.CharField(
        max_length=100, widget=forms.HiddenInput(), required=False
    )
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    time_added = forms.DateField(
        label="Time of Day",
        initial=time(int(now.strftime("%H")), int(now.strftime("%M"))),
        widget=forms.TimeInput(format="%H:%M"),
    )
    amount = forms.FloatField(initial=1)
    # TODO: Unit Feature omitted for now
    unit = forms.ChoiceField(choices=UNIT_CHOICES)
