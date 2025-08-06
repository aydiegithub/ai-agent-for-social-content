from django.urls import path
from .views import PricingView, PaymentWebhookView

# The app_name variable helps Django distinguish between URL names
# from different apps.
app_name = 'billing'

urlpatterns = [
    # This maps the root URL of this app (/billing/) to our pricing page
    path('', PricingView.as_view(), name = 'pricing'),
    
    # This creates a dynamic URL to handle incomming webhooks from different gateways.
    # example: /billing/webhook/razorpay or /billing/webhook/stripe/
    # The <str: gateway> part captures the gateway's name and passes it to the view.
    path('webhook/<str:gateway>/', PaymentWebhookView.as_view(), name='webhook'),
]
