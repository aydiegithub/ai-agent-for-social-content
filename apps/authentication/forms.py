from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class CustomUserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus password validation.
    """
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password"
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    ) 
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number')
        
    def clean_confirm_password(self):
        """
        Custom validation to ensure that the two password fields match
        """
        password = self.cleaned_data.get('password')
        confirm_password = self.confirm_password.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Password don't match")
        return confirm_password
    
    def clean_email(self):
        """
        custom validation to ensure the email adress is unique.
        
        NOTE: This check relies on Django's ORM. For D1, we will need to adapt
        this to perform a direct lookup, but the form structure remains valid.
        """
        
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
    
class OTPVerificationForm(forms.ModelForm):
    """
    A Simple form to handle the 6 digit OTP input from the user.
    """
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit code'})
    )
    

class CustomLoginForm(AuthenticationForm):
    """
    A custom login form
    Inherits all functionality from Django's built-in AuthenticationForm    
    """
    
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', # Example for later styling
                'placeholder': 'Username or Email'
        })
    )
    
    password = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }
        )
    )