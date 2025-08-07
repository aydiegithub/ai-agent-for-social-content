from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class CustomUserCreationForm(forms.ModelForm):
    # ... (password and other field definitions remain the same) ...
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

    # --- ADD THIS __init__ METHOD ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define the common Tailwind CSS classes
        tailwind_classes = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
        
        # Add the classes to all fields except for the date picker
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({'class': tailwind_classes})
            # Add placeholders based on field name
            field.widget.attrs.update({'placeholder': field.label})

    # ... (clean_confirm_password and save methods remain the same) ...
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


class CustomLoginForm(AuthenticationForm):
    # ... (no changes needed here) ...
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Password'
    }))

class OTPVerificationForm(forms.Form):
    # ... (no changes needed here) ...
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 text-center tracking-[1em] border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': '------'
        })
    )