from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model for the project.

    It's best practice to start with a custom user model.
    Future fields like 'avatar' or 'phone_number' can be added here.
    """

    pass


class TimeStampedModel(models.Model):
    """
    An abstract base model that provides self-updating `created_at` and
    `updated_at` fields.
    """

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True  # This ensures no database table is created for this model.
