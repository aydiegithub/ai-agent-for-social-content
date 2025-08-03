from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Django's built-in admin site
    path('admin/', admin.site.urls),
    
    # Include all URLs from the authentication app under the 'auth/' prefix.
    # For example, the signup view will be available at /auth/signup/
    path('auth/', include('apps.authentication.urls', namespace='authentication')),
    
    # Include all URLs from the dashboard app under the 'dashboard/' prefix.
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    
    # Adding other app URLs here as we build them
    # path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    # path('billing/', include('apps.billing.urls', namespace='billing')),
    # path('social/', include('apps.social.urls', namespace='social')),
    
    # For the root URL ('/'), redirect to the login page.
    # This makes the login page the default entry point for visitors.
    path('', RedirectView.as_view(pattern_name='authentication:login', permanent=False)),
]