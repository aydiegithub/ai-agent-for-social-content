from django.db import models
from django.contrib.auth.models import AbstractUser

# Because we are using CloudFlare D1 as our database, Django's built-in
# migration system (`makemigrations`, `migrate`) will NOT be used to create
# or alter the database schema. The source of truth for the database schema
# is the raw SQL file in `migrations/0001_initial.sql`.
#
# These Django models serve as a Python-native representation of our D1 tables.
# They are crucial for:
# 1. Data Validation: Using Django Forms and Serializers.
# 2. Business Logic: Interacting with user data in a structured way in our views.
# 3. Code Clarity: Providing a clear, object-oriented definition of our data.

class User(AbstractUser):
    """
    Custom User model that extends Django's built-in AbstractUser
    This model mirrors the 'users' table defined in our D1 SQL migration.
    """
    # AbstractUser already provides
    # username, first_name, last_name, email, passwords,
    # is_staff, is_active, is_superuser, last_login, date_joined
    
    # we will overide the email field to make it unique and always required
    email = models.EmailField(unique=True, blank=False, null=False)
    
    # Custom fields to match our D1 schema
    phone_number = models.CharField(max_length=20, unique=True, blank=False, null=True)
    email_otp = models.CharField(max_length=6, blank=True, null=True)
    sms_otp = models.CharField(max_length=6, blank=True, null=True)
    
    # We use a boolean field here which will map to the INTEGER type in D1 (0 or 1)
    is_verified = models.BooleanField(default=False)
    
    
    # We can use the 'date_joined' field AbstractUser for 'created_at'
    def __str__(self):
        """
        String reperesents the user object.
        """
        return self.username