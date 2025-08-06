from django.db import models
from django.conf import settings

# This model mirrors the `social_connections` table in our D1 SQL schema.
# It is not used for database migrations but for data validation, serialization,
# and providing an object-oriented interface to our data within Django.

class SocialConnnection(models.Model):
    """
    Stores the OAuth tokens and connection details for a user's social media accounts.
    """  
    
    PLATFORM_CHOICES = [
        ('X.com', 'X.com'),
        ('LinkedIn', 'LinkedIn')
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_connections'
    )
    
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        help_text="The social media platform."
    )
    
    # In a production environment, these tokens MUST be encrypted before
    # being saved to the database. We use a library 'cryptography'
    # and custom model field methods to handle this automatically.
    # For now, we store them as text.
    access_token = models.TextField(
        help_text="The encrypted OAuth accedd token."
    )
    
    refresh_token = models.TextField(
        blank=True,
        null=True,
        help_text="The encrypted OAuth refresh token, if provided."
    )
    
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The timestamp when the access token expires."
    )
    
    profile_id = models.CharField(
        max_length=255,
        help_text="The user's unique ID or handle on the social platform."
    )
    
    class Meta:
        # This creates a composite primary key, ensuring that a user can only
        # have one entry per platform.
        unique_together = ('user', 'platform')
        verbose_name_plural = "Socail Connections"
        
    def __str__(self):
        """
        String representation of a social connection.
        """
        return f"{self.user.username}'s {self.get_platform_display()} Connection"     
    