from django.db import models
from django.conf import settings
from .encryption import encrypt_token, decrypt_token

class SocialConnection(models.Model):
    """
    Stores the OAuth tokens and connection details for a user's social media accounts.
    Tokens are encrypted at rest in the database.
    """  
    
    PLATFORM_CHOICES = [
        ('x_com', 'X.com'),
        ('linkedin', 'LinkedIn')
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
    
    # These fields will store the ENCRYPTED tokens.
    _access_token = models.TextField(
        db_column='access_token',
        help_text="The encrypted OAuth access token."
    )
    
    _refresh_token = models.TextField(
        db_column='refresh_token',
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

    # We use properties to handle encryption/decryption on the fly.
    # The application code will interact with `access_token` and `refresh_token`
    # without needing to know about the encryption.
    
    @property
    def access_token(self):
        return decrypt_token(self._access_token)

    @access_token.setter
    def access_token(self, value):
        self._access_token = encrypt_token(value)

    @property
    def refresh_token(self):
        return decrypt_token(self._refresh_token)

    @refresh_token.setter
    def refresh_token(self, value):
        self._refresh_token = encrypt_token(value)
    
    class Meta:
        # This ensures that a user can only have one connection per platform.
        unique_together = ('user', 'platform')
        verbose_name_plural = "Social Connections"
        
    def __str__(self):
        """
        String representation of a social connection.
        """
        return f"{self.user.username}'s {self.get_platform_display()} Connection"