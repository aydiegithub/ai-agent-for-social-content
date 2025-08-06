import os
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from requests_oauthlib import OAuth2Session

from .models import SocialConnection
from apps.dashboard.models import ContentHistory
from apps.billing.models import Credits

# --- OAuth Configuration ---
# In a real application, these would be loaded securely from environment variables.
# We are defining them here for clarity.
# You would get these values by creating a developer app on X.com and LinkedIn.
OAUTH_CONFIG = {
    'x_com': {
        'client_id': os.getenv('X_CLIENT_ID', 'YOUR_X_CLIENT_ID'),
        'client_secret': os.getenv('X_CLIENT_SECRET', 'YOUR_X_CLIENT_SECRET'),
        'authorization_url': 'https://twitter.com/i/oauth2/authorize',
        'token_url': 'https://api.twitter.com/2/oauth2/token',
        'scopes': ['tweet.read', 'tweet.write', 'users.read', 'offline.access'],
        'user_info_url': 'https://api.twitter.com/2/users/me',
    },
    'linkedin': {
        'client_id': os.getenv('LINKEDIN_CLIENT_ID', 'YOUR_LINKEDIN_CLIENT_ID'),
        'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET', 'YOUR_LINKEDIN_CLIENT_SECRET'),
        'authorization_url': 'https://www.linkedin.com/oauth/v2/authorization',
        'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
        'scopes': ['profile', 'w_member_social'], # Correct scopes for posting
        'user_info_url': 'https://api.linkedin.com/v2/userinfo',
    }
}


class SocialConnectionsView(LoginRequiredMixin, View):
    """
    Displays the user's current social media connections and allows them to add more.
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

        # Create an OAuth2 session object
        oauth = OAuth2Session(
            config['client_id'],
            redirect_uri=callback_url,
            scope=config['scopes']
        )
        
        # Generate the authorization URL and a state token for security
        authorization_url, state = oauth.authorization_url(config['authorization_url'])
        
        # Store the state in the user's session to verify it on callback
        request.session[f'{platform}_oauth_state'] = state
        
        print(f"SIMULATION: Redirecting user to: {authorization_url}")
        return redirect(authorization_url)


class OAuthCallbackView(LoginRequiredMixin, View):
    """
    Handles the callback from the social platform after user authorization.
    """
    def get(self, request, platform, *args, **kwargs):
        if platform not in OAUTH_CONFIG:
            messages.error(request, "Invalid social platform specified.")
            return redirect('social:connections')

        # --- SIMULATION: We don't have a real code, so we'll skip the API call ---
        # In a real flow, you would uncomment and use the code below.
        # For now, we will simulate a successful connection.
        
        # try:
        #     config = OAUTH_CONFIG[platform]
        #     callback_url = request.build_absolute_uri(reverse('social:oauth_callback', args=[platform]))
            
        #     oauth = OAuth2Session(
        #         config['client_id'],
        #         redirect_uri=callback_url,
        #         state=request.session.get(f'{platform}_oauth_state')
        #     )
            
        #     # Exchange the authorization code for an access token
        #     token = oauth.fetch_token(
        #         config['token_url'],
        #         client_secret=config['client_secret'],
        #         authorization_response=request.build_absolute_uri()
        #     )

        #     # Fetch user info from the platform's API
        #     user_info_response = oauth.get(config['user_info_url'])
        #     user_info = user_info_response.json()
        #     profile_id = user_info.get('id') or user_info.get('data', {}).get('username')

        # except Exception as e:
        #     messages.error(request, f"An error occurred during authentication: {e}")
        #     return redirect('social:connections')

        # --- SIMULATED SUCCESSFUL CONNECTION ---
        print(f"SIMULATION: Callback received for {platform.upper()}.")
        token = {
            'access_token': 'simulated_access_token_for_' + platform,
            'refresh_token': 'simulated_refresh_token_for_' + platform,
            'expires_in': 3600
        }
        profile_id = f'simulated_{request.user.username}'
        print(f"SIMULATION: Fetched token and user profile ID '{profile_id}'.")
        # --- END SIMULATION ---

        # Save the connection details to the database
        SocialConnection.objects.update_or_create(
            user=request.user,
            platform=platform,
            defaults={
                'access_token': token['access_token'],
                'refresh_token': token.get('refresh_token'),
                'profile_id': profile_id,
                # TODO: Calculate and store expires_at timestamp
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
            return redirect('dashboard:dashboard') # Or the content detail page

        # 2. Get the content and the social connection
        try:
            content = ContentHistory.objects.get(id=content_id, user=request.user)
            connection = SocialConnection.objects.get(user=request.user, platform=platform)
        except (ContentHistory.DoesNotExist, SocialConnection.DoesNotExist):
            messages.error(request, "Could not find the content or social connection.")
            return redirect('dashboard:dashboard')

        # 3. TODO: Implement the actual API call to post the content
        #    - Create an OAuth2Session with the stored token.
        #    - Handle token refresh if necessary.
        #    - Format the content for the platform (e.g., character limits).
        #    - Make the POST request to the platform's API endpoint.
        
        print(f"SIMULATION: Posting content ID {content.id} to {platform.upper()} for user {request.user.username}.")
        print(f"--- CONTENT ---\n{content.generated_text[:280]}...\n---------------")

        # 4. Deduct credit and update content status
        user_credits.balance -= 1
        user_credits.save()

        # Update status (this logic could be more robust for multiple platforms)
        if content.status == 'DRAFT':
            content.status = f'POSTED_{platform.upper()}'
        elif 'POSTED' in content.status:
            content.status = 'POSTED_ALL'
        content.save()

        messages.success(request, f"Content successfully posted to {platform.replace('_', ' ').title()}!")
        return redirect('dashboard:dashboard')