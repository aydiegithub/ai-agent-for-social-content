from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Django's built-in admin site.
    path('admin/', admin.site.urls),

    # Include all URLs from the authentication app under the 'auth/' prefix.
    path('auth/', include('apps.authentication.urls', namespace='authentication')),
    
    # Include all URLs from the dashboard app under the 'dashboard/' prefix.
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    
    # Include all URLs from the billing app under the 'billing/' prefix.
    path('billing/', include('apps.billing.urls', namespace='billing')),
    
    # Include all URLs from the social app under the 'social/' prefix.
    path('social/', include('apps.social.urls', namespace='social')),

    # For the root URL ('/'), redirect to the dashboard.
    # The LoginRequiredMixin on the DashboardView will automatically handle
    # redirecting unauthenticated users to the login page.
    path('', RedirectView.as_view(pattern_name='dashboard:dashboard', permanent=False)),
]