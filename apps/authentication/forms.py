from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class CustomUserCreationForm(forms.ModelForm):
    """
    An expanded form for creating new users with detailed profile information.
    """
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'email', 
            'date_of_birth', 'gender', 'profession', 
            'how_did_you_hear_about_us', 'referral_code', 'country', 'interests'
        )

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

# --- ADD THE MISSING FORMS BELOW ---

class CustomLoginForm(AuthenticationForm):
    """A standard login form with Tailwind CSS classes."""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Password'
    }))

class OTPVerificationForm(forms.Form):
    """A form for the 6-digit OTP code."""
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 text-center tracking-[1em] border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': '------'
        })
    )