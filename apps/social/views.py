import os
import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.utils.timezone import now
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import WebApplicationClient

from .models import SocialConnection
from apps.dashboard.models import ContentHistory
from apps.billing.models import Credits

# --- OAuth Configuration ---
# These values MUST be set in your environment variables.
OAUTH_CONFIG = {
    'x_com': {
        'client_id': os.getenv('X_CLIENT_ID'),
        'client_secret': os.getenv('X_CLIENT_SECRET'),
        'authorization_url': 'https://twitter.com/i/oauth2/authorize',
        'token_url': 'https://api.twitter.com/2/oauth2/token',
        'scopes': ['tweet.read', 'tweet.write', 'users.read', 'offline.access'],
        'user_info_url': 'https://api.twitter.com/2/users/me',
        'post_tweet_url': 'https://api.twitter.com/2/tweets',
    },
    'linkedin': {
        'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
        'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET'),
        'authorization_url': 'https://www.linkedin.com/oauth/v2/authorization',
        'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
        'scopes': ['profile', 'w_member_social', 'openid'],
        'user_info_url': 'https://api.linkedin.com/v2/userinfo',
    }
}


class SocialConnectionsView(LoginRequiredMixin, View):
    """
    Displays the user's current social media connections.
    """
    template_name = 'social/connections.html'

    def get(self, request, *args, **kwargs):
        connections = SocialConnection.objects.filter(user=request.user)
        context = {
            'connections': {conn.platform: conn for conn in connections}
        }
        return render(request, self.template_name, context)


class OAuthRedirectView(LoginRequiredMixin, View):
    """
    Initiates the OAuth2 flow by redirecting the user to the social platform.
    """
    def get(self, request, platform, *args, **kwargs):
        if platform not in OAUTH_CONFIG:
            messages.error(request, "Invalid social platform specified.")
            return redirect('social:connections')

        config = OAUTH_CONFIG[platform]
        callback_url = request.build_absolute_uri(reverse('social:oauth_callback', args=[platform]))

        oauth = OAuth2Session(
            config['client_id'],
            redirect_uri=callback_url,
            scope=config['scopes'],
        )
        
        # For X.com, PKCE is required for security.
        code_verifier = WebApplicationClient(config['client_id']).create_code_verifier(60)
        request.session['code_verifier'] = code_verifier
        code_challenge = WebApplicationClient(config['client_id']).create_code_challenge(code_verifier, "S256")
        
        authorization_url, state = oauth.authorization_url(
            config['authorization_url'],
            code_challenge=code_challenge,
            code_challenge_method="S256"
        )
        
        request.session[f'{platform}_oauth_state'] = state
        return redirect(authorization_url)


class OAuthCallbackView(LoginRequiredMixin, View):
    """
    Handles the callback from the social platform after user authorization.
    Exchanges the authorization code for an access token.
    """
    def get(self, request, platform, *args, **kwargs):
        if platform not in OAUTH_CONFIG:
            messages.error(request, "Invalid social platform specified.")
            return redirect('social:connections')

        try:
            config = OAUTH_CONFIG[platform]
            callback_url = request.build_absolute_uri(reverse('social:oauth_callback', args=[platform]))
            
            oauth = OAuth2Session(
                config['client_id'],
                redirect_uri=callback_url,
                state=request.session.get(f'{platform}_oauth_state')
            )
            
            # Fetch the token from the platform's token URL.
            token = oauth.fetch_token(
                config['token_url'],
                client_secret=config['client_secret'],
                authorization_response=request.build_absolute_uri(),
                code_verifier=request.session.get('code_verifier')
            )

            # Fetch user info from the platform's API to get their ID/username.
            user_info_response = oauth.get(config['user_info_url'])
            user_info = user_info_response.json()
            
            # Extract profile ID differently based on platform
            if platform == 'x_com':
                profile_id = user_info.get('data', {}).get('username', 'Unknown')
            elif platform == 'linkedin':
                profile_id = user_info.get('sub', 'Unknown') # LinkedIn uses 'sub' for user ID
            else:
                profile_id = 'Unknown'

            # Calculate when the token will expire.
            expires_at_timestamp = now() + timedelta(seconds=token.get('expires_in', 3600))

        except Exception as e:
            messages.error(request, f"An error occurred during authentication: {e}")
            return redirect('social:connections')

        # Save the connection details to the database using our encrypted model.
        SocialConnection.objects.update_or_create(
            user=request.user,
            platform=platform,
            defaults={
                'access_token': token['access_token'],
                'refresh_token': token.get('refresh_token'),
                'profile_id': profile_id,
                'expires_at': expires_at_timestamp,
            }
        )
        
        messages.success(request, f"Successfully connected your {platform.replace('_', ' ').title()} account!")
        return redirect('social:connections')


class PostToSocialView(LoginRequiredMixin, View):
    """
    Handles the action of posting a piece of content to a social platform.
    """
    def post(self, request, content_id, platform, *args, **kwargs):
        # 1. Check user credits (1 credit per post)
        user_credits = Credits.objects.get(user=request.user)
        if user_credits.balance < 1:
            messages.error(request, "You don't have enough credits to post.")
            return redirect('dashboard:dashboard')

        # 2. Get the content and the social connection
        try:
            content = ContentHistory.objects.get(id=content_id, user=request.user)
            connection = SocialConnection.objects.get(user=request.user, platform=platform)
        except (ContentHistory.DoesNotExist, SocialConnection.DoesNotExist):
            messages.error(request, "Could not find the content or social connection.")
            return redirect('dashboard:dashboard')

        # 3. Post the content using the stored token
        try:
            config = OAUTH_CONFIG[platform]
            
            # The token is automatically decrypted when we access `connection.access_token`
            token_dict = {'access_token': connection.access_token, 'token_type': 'Bearer'}
            client = OAuth2Session(config['client_id'], token=token_dict)
            
            # Example for posting to X.com
            if platform == 'x_com':
                payload = {"text": content.generated_text}
                response = client.post(config['post_tweet_url'], json=payload)
                if response.status_code != 201:
                    raise Exception(f"API Error: {response.text}")
            
            # TODO: Add logic for other platforms like LinkedIn here.
            
        except Exception as e:
            messages.error(request, f"Failed to post to {platform.title()}. Error: {e}")
            return redirect('dashboard:dashboard')

        # 4. Deduct credit and update content status
        user_credits.balance -= 1
        user_credits.save()

        if content.status == 'DRAFT':
            content.status = f'POSTED_{platform.upper()}'
        elif 'POSTED' in content.status:
            content.status = 'POSTED_ALL'
        content.save()

        messages.success(request, f"Content successfully posted to {platform.replace('_', ' ').title()}!")
        return redirect('dashboard:dashboard')