from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    email = models.EmailField(
        verbose_name='E-mail',
        unique=True,
        max_length=254,
        blank=False
    )
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=150, blank=False)