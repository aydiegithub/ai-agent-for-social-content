from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views import View
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm, OTPVerificationForm, CustomLoginForm
from .models import User
from apps.billing.models import Credits

import random

# --- Helper Function ---
def generate_otp():
    """Generates a 6-digit random OTP."""
    return str(random.randint(100000, 999999))

class SignUpView(View):
    """
    Handles user registration using standard Django forms and ORM.
    """
    form_class = CustomUserCreationForm
    template_name = 'authentication/signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # The form now handles saving the user and hashing the password.
            user = form.save(commit=False)
            user.is_active = False # User cannot log in until verified
            user.save()

            # Create the initial credits for the new user.
            Credits.objects.create(user=user, balance=10)

            # TODO: Implement a real email sending service here.
            otp = generate_otp()
            # In a real app, you'd save this OTP to a temporary cache or model field
            # and email it to the user. For now, we'll simulate.
            print(f"OTP for {user.email} is: {otp}")
            request.session['otp_for_verification'] = otp
            request.session['unverified_user_id'] = user.id
            
            messages.success(request, 'Registration successful! Please check your email for an OTP.')
            return redirect('authentication:verify_otp')

        return render(request, self.template_name, {'form': form})


class VerifyOTPView(View):
    """
    Handles OTP verification using the Django ORM.
    """
    form_class = OTPVerificationForm
    template_name = 'authentication/verify_otp.html'

    def get(self, request, *args, **kwargs):
        if 'unverified_user_id' not in request.session:
            return redirect('authentication:signup')
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('unverified_user_id')
        correct_otp = request.session.get('otp_for_verification')
        if not user_id or not correct_otp:
            return redirect('authentication:signup')

        form = self.form_class(request.POST)
        if form.is_valid():
            if form.cleaned_data['otp'] == correct_otp:
                try:
                    user = User.objects.get(id=user_id)
                    user.is_active = True
                    user.is_verified = True
                    user.save()

                    # Clean up session
                    del request.session['unverified_user_id']
                    del request.session['otp_for_verification']

                    login(request, user)
                    messages.success(request, 'Your account has been verified successfully!')
                    return redirect('dashboard:dashboard')
                except User.DoesNotExist:
                    messages.error(request, 'User not found. Please sign up again.')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        
        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    """
    Standard login view. No changes needed here.
    """
    form_class = CustomLoginForm
    template_name = 'authentication/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard:dashboard')

def logout_view(request):
    """
    Standard logout view. No changes needed here.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('authentication:login')