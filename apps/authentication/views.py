from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views import View
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm, OTPVerificationForm, CustomLoginForm
from .models import User

# from .utils import send_otp_email

import random

def generate_otp():
    """Generate a 6-digit random OTP."""
    return str(random.randint(100000, 999999))

class RegisterView(View):
    """
    Handles user registration.
    """
    form_class = CustomUserCreationForm
    template_name = 'authentication/signup.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # Create the user object
            user = form.save(commit=False)
            # Set password correctly
            user.set_password(form.cleaned_data['password'])
            # User is not active until OTP is verified
            user.is_active = False

            # Generate and store OTP
            otp = generate_otp()
            user.email_otp = otp
            
            # D1 DATABASE
            # The user.save() call will eventually be translated by our custom
            # database backend into an INSERT query to the D1 'users' table.
            user.save()
            
            # Integrate with a real email service
            # send_otp_email(user.email, otp)
            print(f"OTP for {user.email} is: {otp}") # Remove after testing
            request.session['unverified_user_id'] = user.id
            
            messages.success(request, 'Registration successful! Please check your email for an OTP.')
            return redirect('verify_otp') # Edit this later
        
        return render(request, self.template_name, {'form': form})
    
class VerifyOTPView(View):
    """
    Handles OTP verification for new users.
    """
    
    form_class = OTPVerificationForm
    template_name = "authentication/verify_otp.html"
    
    def get(self, request, *args, **kwargs):
        if 'unverified_user_id' not in request.session:
            messages.error(request, 'No user to verify. Please sign up first.')
            return redirect('signup') # We will name this URL later
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
        
        
    def post(self, request, *args, **kwargs):
        user_id = request.session.get('unverified_user_id')
        if not user_id:
            messages.error(request, 'Your session has expired. Please sign up again.')
            return redirect('signup')
        
        try:
            # D1 DATABASE NOTE:
            # This User.objects.get() call will be translated into a
            # SELECT query on the D1 'users' table.
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, 'User not found. Please sign up again.')
            return redirect('signup')
        
        form = self.form_class(request.POST)
        if form.is_valid():
            if user.email_otp == form.cleaned_data['otp']:
                user.is_active = True
                user.is_verified = True
                user.email_otp = None # Clear OTP after successful verification
                user.save() # This will be an UPDATE query to D1
                
                # Log the user in automatically
                login(request, user)
                
                # Clean up the session
                del request.session['unverified_user_id']
                
                messages.success(request, 'Your account has been verified successfully!')
                return redirect('dashboard') # We will name this URL later
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                
        return render(request, self.template_name, {'form': form})
    

class CustomLoginView(LoginView):
    """ 
    Custom login view to use our custom form and template
    """
    form_class = CustomLoginForm
    template_name = 'authentication/login.html'
    
    def get_success_url(self):
        # Redirect to the dashboard
        return reverse_lazy('dashboard') # CHange the url later
    
def logout_view(request):
    """ 
    Logs the user out and redirectd to the login page.
    """
    logout(request)
    messages.info(request, 'You have logged out successfully.')
    return redirect('login') # We will name this URL later
            
            
            