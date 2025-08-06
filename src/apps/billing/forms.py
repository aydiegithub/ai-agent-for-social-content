from django import forms

class CreditPurchaseForm(forms.Form):
    """ 
    A form to handle the user's selection of a credit package.add()
    
    This form is simple, but it provides a layer of validation to ensure
    that the plan ID submitted by the user is a valid one.
    """
    
    # In a real application, these choices might be populated dynamically
    # from a database model or a configuraion file.
    
    PLAN_CHOICES = [
        ('starter_usd', 'Starter (USD)'),
        ('creator_usd', 'Creator (USD)'),
        ('business_usd', 'Business (USD)'),
        ('pro_usd', 'Pro (USD)'),
        ('starter_inr', 'Starter (INR)'),
        ('creator_inr', 'Creator (INR)'),
        ('business_inr', 'Business (INR)'),
        ('pro_inr', 'Pro (INR)'),  
    ]
    
    plan_id = forms.ChoiceField(
        choices=PLAN_CHOICES,
        required=True,
        widget=forms.HiddenInput() # The user selects a plan by clicking a button, not from a dropdown.
    )