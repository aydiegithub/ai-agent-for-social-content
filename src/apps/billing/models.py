from django.db import models
from django.conf import settings # reference the User model
from utils.logger import logging

# These models mirror the `credits` and `transactions` tables in our D1 SQL schema.
# They are not used for database migrations but for data validation, serialization,
# and providing an object-oriented interface to our data within Django.

class Credits(models.Model):
    """
    Represents the credit balance for single user.
    """
    
    # Using a OneToOneField creates a direct, unique link to a user.
    # It's more efficient and logical than a ForeignKey for a profile-like model.
    # settings.AUTH_USER_MODEL is the correct way to reference the User model
    # in case it's ever changed in the settings.
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True # Makes the user_id the primary key of this table.
    )
    
    balance = models.IntegerField(
        default=15, # New users start with 15 free credits.
        help_text="The current credit balance of the user."
    )
    
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="The timestamp when the balance was last updated"
    )
    
    def __str__(self):
        """
        String representation of user's credit balance.
        """
        logging.info(f"Credits accessed for user: {self.user.username} with balance: {self.balance}")
        return f"{self.user.username} - {self.balance} credits."
    
    class Meta:
        verbose_name_plural = 'Credits'
        


class Transaction(models.Model):
    """
    Logs every payment transaction mode by the users to purchase credits.
    """
    
    # Choices for fields to ensure data integrity
    GATEWAY_CHOICES = [
        ('PAYPAL', 'PayPal'),
        ('PAYONEER', 'Payoneer'),
        ('RAZORPAY', 'Razorpay'), # For UPI and others
        ('STRIPE', 'Stripe'), 
    ]
    
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('INR', 'Indian Rupee'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transactions'
    )
    
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    gateway_txn_id = models.CharField(max_length=255, unique=True)
    
    # Using DecimalField is crucial for financial calculation
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    credits_purchased = models.IntegerField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True) # Automatically set on creation.
    
    
    def __str__(self):
        """
        String representation of a transaction.
        """
        logging.info(f"Transaction accessed: {self.gateway_txn_id} for user: {self.user.username if self.user else 'Unknown'} with status: {self.status}")
        return f"Txn {self.gateway_txn_id} by {self.user.username if self.user else 'Unknown'} - {self.status}"
