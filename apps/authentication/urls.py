# URLs for the authentication app.
from django.urls import path
from .views import SignUpView, CustomLoginView, VerifyOTPView, logout_view

# The app_name variable helps Django distinguish between URL names
# from different apps. For example, you can have a 'detail' view
# in multiple apps and Django will know which one to use.
app_name = 'authentication'

urlpatterns = [
    # URL for user registration
    path('signup/', SignUpView.as_view(), name='signup'),

    # URL for user login
    path('login/', CustomLoginView.as_view(), name='login'),

    # URL for user logout
    path('logout/', logout_view, name='logout'),

    # URL for OTP verification
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
]