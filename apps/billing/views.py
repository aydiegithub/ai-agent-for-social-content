import os
import json
import hmac
import hashlib
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.db import transaction

from .forms import CreditPurchaseForm
from .models import Transaction, Credits

# --- Pricing Configuration ---
PRICING_PLANS = {
    'usd': [
        {'id': 'starter_usd', 'name': 'Starter', 'price': 2.99, 'credits': 50, 'currency': 'USD'},
        {'id': 'creator_usd', 'name': 'Creator', 'price': 9.99, 'credits': 200, 'currency': 'USD'},
    ],
    'inr': [
        {'id': 'starter_inr', 'name': 'Starter', 'price': 199, 'credits': 50, 'currency': 'INR'},
        {'id': 'creator_inr', 'name': 'Creator', 'price': 699, 'credits': 200, 'currency': 'INR'},
    ]
}

def get_country_from_request(request):
    """Simulates GeoIP lookup."""
    return 'IN' # Default to India for your case

class PricingView(LoginRequiredMixin, View):
    template_name = 'billing/pricing.html'
    form_class = CreditPurchaseForm
    
    def get(self, request, *args, **kwargs):
        country_code = get_country_from_request(request)
        currency = 'inr' if country_code == 'IN' else 'usd'
        context = {'plans': PRICING_PLANS[currency], 'form': self.form_class()}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            messages.error(request, "Invalid plan selected.")
            return redirect('billing:pricing')

        plan_id = form.cleaned_data['plan_id']
        selected_plan = next((p for p in PRICING_PLANS['usd'] + PRICING_PLANS['inr'] if p['id'] == plan_id), None)
        
        if not selected_plan:
            messages.error(request, "Invalid plan selected.")
            return redirect('billing:pricing')
        
        # TODO: Integrate with a real payment gateway API to create an order.
        # The gateway would return an order_id (gateway_txn_id).
        # For now, we'll simulate this.
        gateway_txn_id = f"sim_{hmac.new(os.urandom(16), digestmod=hashlib.sha256).hexdigest()}"
        
        Transaction.objects.create(
            user=request.user,
            gateway='RAZORPAY', # Or determine dynamically
            gateway_txn_id=gateway_txn_id,
            amount=selected_plan['price'],
            currency=selected_plan['currency'],
            credits_purchased=selected_plan['credits'],
            status='PENDING'
        )
        
        messages.info(request, "SIMULATION: Redirecting to payment gateway...")
        # In a real app, you would redirect to the gateway's checkout URL.
        # You can manually trigger the webhook for testing.
        return redirect('billing:pricing')

@method_decorator(csrf_exempt, name='dispatch')
class PaymentWebhookView(View):
    """
    Handles incoming webhooks from payment gateways to confirm transactions.
    This view MUST be protected by signature verification.
    """
    def post(self, request, gateway, *args, **kwargs):
        # This secret key is provided by your payment gateway dashboard.
        # It MUST be set in your environment variables.
        webhook_secret = os.getenv(f"{gateway.upper()}_WEBHOOK_SECRET")
        if not webhook_secret:
            print(f"ERROR: Webhook secret for {gateway.upper()} is not configured.")
            return HttpResponse(status=500)

        # --- Signature Verification (Example for Razorpay) ---
        try:
            # Get the signature from the request headers
            signature = request.headers.get('X-Razorpay-Signature')
            if not signature:
                return HttpResponseBadRequest("Signature missing.")
            
            # Verify the signature
            generated_signature = hmac.new(webhook_secret.encode(), request.body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(generated_signature, signature):
                return HttpResponseBadRequest("Invalid signature.")
        except Exception as e:
            print(f"ERROR: Signature verification failed: {e}")
            return HttpResponseBadRequest("Invalid request.")
        # --- End Verification ---
        
        try:
            payload = json.loads(request.body)
            event_type = payload.get('event')

            # We only care about successful payment events
            if event_type == 'payment.captured' or event_type == 'order.paid':
                # Get the transaction ID from the payload
                payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
                gateway_txn_id = payment_entity.get('order_id') or payment_entity.get('id')

                if not gateway_txn_id:
                    return HttpResponseBadRequest("Transaction ID missing in payload.")

                with transaction.atomic():
                    # Find the corresponding transaction in our database
                    txn_to_update = Transaction.objects.select_for_update().get(
                        gateway_txn_id=gateway_txn_id, status='PENDING'
                    )
                    
                    # Update its status to 'COMPLETED'
                    txn_to_update.status = 'COMPLETED'
                    txn_to_update.save()
                    
                    # Add the purchased credits to the user's account
                    user_credits, _ = Credits.objects.get_or_create(user=txn_to_update.user)
                    user_credits.balance += txn_to_update.credits_purchased
                    user_credits.save()
                    
                print(f"SUCCESS: Processed webhook for Txn ID: {gateway_txn_id}")
            else:
                print(f"INFO: Received unhandled event type: {event_type}")

        except Transaction.DoesNotExist:
            print(f"ERROR: Received webhook for an unknown or already processed transaction.")
            return HttpResponseBadRequest("Transaction not found or already processed.")
        except Exception as e:
            print(f"ERROR: An error occurred processing webhook: {e}")
            return HttpResponse(status=500)
        
        # Return a 200 OK to the gateway to acknowledge receipt.
        return HttpResponse(status=200)