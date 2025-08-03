from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add app-specific URLs here
    # path('auth/', include('apps.authentication.urls')),
]
