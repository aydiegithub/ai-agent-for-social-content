from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model with additional profile information.
    """
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    # We override the email field to ensure it's always unique.
    email = models.EmailField(unique=True, blank=False, null=False)

    # New profile fields you requested
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    profession = models.CharField(max_length=100, null=True, blank=True)
    how_did_you_hear_about_us = models.CharField(max_length=255, null=True, blank=True)
    referral_code = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    interests = models.TextField(null=True, blank=True, help_text="Comma-separated interests.")

    # Fields from the old D1 schema that are still relevant
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username