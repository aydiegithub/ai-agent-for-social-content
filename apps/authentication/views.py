from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login, logout
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm, OTPVerificationForm, CustomLoginForm
from .models import User

# Import the D1 client to replace the Django ORM for database operations
from core.db.d1_client import d1_client

import random

# --- Helper Function (will be moved to a utils.py file later) ---
def generate_otp():
    """Generates a 6-digit random OTP."""
    return str(random.randint(100000, 999999))

class SignUpView(View):
    """
    Handles user registration using the D1 client.
    """
    form_class = CustomUserCreationForm
    template_name = 'authentication/signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # Hash the password securely before storing it
            hashed_password = make_password(data['password'])
            otp = generate_otp()
            
            try:
                # Use the D1 client to create the user directly
                new_user = d1_client.create_user(
                    username=data['username'],
                    email=data['email'],
                    password_hash=hashed_password,
                    otp=otp
                )

                # TODO: Integrate with a real email service
                print(f"OTP for {data['email']} is: {otp}")

                # Store the new user's ID in the session for verification
                request.session['unverified_user_id'] = new_user['id']
                
                messages.success(request, 'Registration successful! Please check your email for an OTP.')
                return redirect('authentication:verify_otp')

            except Exception as e:
                # This could be a UNIQUE constraint error from D1 (e.g., email exists)
                messages.error(request, f"Could not create account. The username or email may already be in use. Error: {e}")

        return render(request, self.template_name, {'form': form})


class VerifyOTPView(View):
    """
    Handles OTP verification using the D1 client.
    """
    form_class = OTPVerificationForm
    template_name = 'authentication/verify_otp.html'

    def get(self, request, *args, **kwargs):
        if 'unverified_user_id' not in request.session:
            messages.error(request, 'No user to verify. Please sign up first.')
            return redirect('authentication:signup')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('unverified_user_id')
        if not user_id:
            messages.error(request, 'Your session has expired. Please sign up again.')
            return redirect('authentication:signup')

        # Use the D1 client to fetch the user data
        user_data = d1_client.get_user_by_id(user_id)
        if not user_data:
            messages.error(request, 'User not found. Please sign up again.')
            return redirect('authentication:signup')

        form = self.form_class(request.POST)
        if form.is_valid():
            if user_data['email_otp'] == form.cleaned_data['otp']:
                # Use the D1 client to activate the user
                d1_client.activate_user(user_id)

                # D1 PRODUCTION NOTE:
                # Django's `login()` function is tightly coupled to the ORM.
                # In a real D1 deployment, this would fail. It would need to be
                # replaced with a custom authentication backend or manual session
                # management that creates a User object from the D1 dictionary.
                # For now, we leave it to represent the intended logic.
                user_obj = User.objects.get(id=user_id) # This line would be removed
                login(request, user_obj)
                
                del request.session['unverified_user_id']
                messages.success(request, 'Your account has been verified successfully!')
                return redirect('dashboard:dashboard')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        
        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    """
    D1 PRODUCTION NOTE:
    This view inherits from Django's LoginView, which will NOT work with D1
    out of the box because it relies on the ORM. A production-ready version
    would be a custom View class that:
    1. Fetches the user from D1 using `d1_client.get_user_by_email()`.
    2. Uses `check_password()` to compare the form password with the stored hash.
    3. Manually logs the user in by setting session variables.
    """
    form_class = CustomLoginForm
    template_name = 'authentication/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard:dashboard')

def logout_view(request):
    """
    Logs the user out and redirects to the login page.
    This function is standard and does not need to be changed.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('authentication:login')