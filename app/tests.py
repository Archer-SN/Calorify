from django.test import Client, TestCase
from .models import *

# Create your tests here.
class FoodTest(TestCase):
    def setup(self):
        user = User.objects.create("")
