"""
User model for the conduit application.

This is a placeholder model that extends Django's AbstractUser.
A custom User model is defined from the start to allow future
customization (e.g., email-based authentication).
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from constants import USER_IMAGE_URL_MAX_LENGTH, USER_BIO_DEFAULT



class User(AbstractUser):
    """
    Custom User model for the RealWorld application.
    Extends Django's AbstractUser to allow future customization.
    """
    bio = models.TextField(blank=True, default=USER_BIO_DEFAULT)
    image = models.URLField(blank=True, default=USER_IMAGE_URL_MAX_LENGTH)


    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username
