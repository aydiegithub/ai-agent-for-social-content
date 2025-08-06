from django.urls import path
from .views import SocialConnectionsView, OAuthRedirectView, OAuthCallbackView, PostToSocialView

# The app_name variable helps Django distinguish between URL names
# from different apps.
app_name = 'social'

urlpatterns = [
    # The main page to view and manage connections
    # e.g., /social/
    path('', SocialConnectionsView.as_view(), name='connections'),

    # The URL to initiate the connection process with a platform
    # e.g., /social/connect/x_com/
    path('connect/<str:platform>/', OAuthRedirectView.as_view(), name='oauth_connect'),

    # The URL the social platform redirects back to after authorization
    # e.g., /social/callback/x_com/
    path('callback/<str:platform>/', OAuthCallbackView.as_view(), name='oauth_callback'),

    # The URL to trigger posting a piece of content to a platform
    # e.g., /social/post/123/x_com/
    path('post/<int:content_id>/<str:platform>/', PostToSocialView.as_view(), name='post_to_social'),
]
