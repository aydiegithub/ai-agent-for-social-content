# URLs for the authentication app.
from django.urls import path
from .views import SignUpView, CustomLoginForm, VerifyOTPView, logout_view