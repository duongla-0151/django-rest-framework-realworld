"""
User model for the conduit application.

This is a placeholder model that extends Django's AbstractUser.
A custom User model is defined from the start to allow future
customization (e.g., email-based authentication).
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for the RealWorld application.

    Extends Django's AbstractUser to allow future customization.
    Currently uses username-based authentication but can be
    extended for email-based auth in later phases.
    """
    email = models.EmailField(unique=True, blank=False)
    bio = models.TextField(blank=True, default='')
    image = models.URLField(blank=True, default='')

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username
