from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.contrib.auth.models import AbstractUser


class Person(AbstractUser):
    """
    Person model
    """

    address = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = PhoneNumberField(blank=True, null=True)
    siblings = models.ManyToManyField(
        "self", blank=True, symmetrical=True, related_name="person_siblings"
    )
    parent = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="person_parent"
    )

    # USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.first_name + " " + self.last_name
