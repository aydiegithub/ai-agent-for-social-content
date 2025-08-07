from django.urls import path # Corrected import
from .views import DashboardView

# The app_name variable helps Django distinguish between URL names
# From different apps

app_name = 'dashboard'

urlpatterns = [
    # This maps the root URL of this app (/dashboard/) to our main view.
    # The name 'dashboard' will be used in templates and redirects.
    path('', DashboardView.as_view(), name='dashboard')
]