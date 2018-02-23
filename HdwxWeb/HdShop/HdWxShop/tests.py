from django.test import TestCase
from . import models
# Create your tests here.

print(models.userrole.objects.get(Rolename = '客户'))
