import json
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
# In a real application, this would likely be stored in the database
# or a more formal configuration file.
PRICING_PLANS = {
    'usd': [
        {'id': 'starter_usd', 'name': 'Starter', 'price': 2.99, 'credits': 50, 'currency': 'USD'},
        {'id': 'creator_usd', 'name': 'Creator', 'price': 9.99, 'credits': 200, 'currency': 'USD'},
        {'id': 'business_usd', 'name': 'Business', 'price': 24.99, 'credits': 600, 'currency': 'USD'},
        {'id': 'pro_usd', 'name': 'Pro', 'price': 49.99, 'credits': 1500, 'currency': 'USD'},
    ],
    'inr': [
        {'id': 'starter_inr', 'name': 'Starter', 'price': 199, 'credits': 50, 'currency': 'INR'},
        {'id': 'creator_inr', 'name': 'Creator', 'price': 699, 'credits': 200, 'currency': 'INR'},
        {'id': 'business_inr', 'name': 'Business', 'price': 1899, 'credits': 600, 'currency': 'INR'},
        {'id': 'pro_inr', 'name': 'Pro', 'price': 3999, 'credits': 1500, 'currency': 'INR'},
    ]
}

def get_country_from_request(request):
    """ 
    Simulates GeoIP lookup to determine the user's country
    In a production environment, use a service like MaxMid GeoIP2 or 
    check header from CDN like Cloudflare (CF-IPCountry)
    """
    # For demonstration, we'll default to 'IN' since you're in India
    # In a real scenario, this would be dynamic.
    # return request.META.get('HTTP_CF_IPCOUNTRY', 'US').upper()
    return 'IN'

class PricingView(LoginRequiredMixin, View):
    """ 
    Display the pricing plans and handles the initiation of a purchase.
    """
    template_name = 'billing/pricing.html'
    form_class = CreditPurchaseForm
    
    def get(self, request, *args, **kwargs):
        country_code = get_country_from_request(request)
        currency = 'inr' if country_code == 'IN' else 'usd'
        plans = PRICING_PLANS[currency]
        
        context = {
            'plans': plans,
            'form': self.form_class()
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        """ 
        This view is called when a user clicks a 'Buy Now' button.
        It creates a pending transcation and redirects to the payment gateway.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            plan_id = form.cleaned_data['plan_id']
            
            # Find the seleccted plan from our configuration
            selected_plan = None
            for plan in PRICING_PLANS['usd'] + PRICING_PLANS['inr']:
                if plan['id'] == plan_id:
                    selected_plan = plan
                    break
            
            if not selected_plan:
                messages.error(request, "Invalid plan selected.")
                return redirect('billing:pricing')
            
            # Create a pending transaction record in the database
            # D1 DATABASE NOTE: This will be an INSERT query.
            transaction_record = Transaction.objects.create(
                user=request.user,
                gateway='RAZORPAY', # Or detrmine dynamically
                amount=selected_plan['price'],
                currency=selected_plan['currency'],
                credits_purchased=selected_plan['credits'],
                status='PENDING'
            )
            
            # TODO: Implement payment gateway logic
            # 1. Call the payment gateway's API (e.g., Razorpay) to create an order.
            # 2. The gateway will return an order_id and details.
            # 3. Update our transaction_record with the gateway_txn_id.
            # 4. Redirect the user to the gateway's checkout page.
            
            messages.info(request, "Redirecting to payment gateway...")
            print(f"SIMULATION: User '{request.user.username}' initiated purchase for plan '{plan_id}'.")
            print(f"SIMULATION: Created pending transaction {transaction_record.id}")
            print(f"SIMULATION: World now redirect to Razorpay/Stripe checkout.")
            
            # For now, we'll just redirect back to the pricing page.
            # In a real app, this would be the gateway's URL.
            return redirect('billing:pricing')
        
        # If form is invalid, re-render the pricing page
        country_code = get_country_from_request(request)
        currency = 'inr' if country_code == 'IN' else 'usd'
        context = {
            'plans': PRICING_PLANS[currency],
            'form': form
        }
        return render(request, self.template_name, context)
    
    
@method_decorator(csrf_exempt, name='dispatch')
class PaymentWebhookView(View):
    """
    Handles incoming webhooks from payment gateways to confirm transaction.
    This view must be accessible by the payment gateway, so CSRF protection is disabled.
    """
    def post(self, request, gateway, *args, **kwargs):
        # TODO: Implement webhook security and logic for each gateway
        # 1. Verify the webhook signature to ensure it's authentic.
        #    This is CRITICAL for security. Each gateway has its own method.
        
        # 2. Parse the webhook payload.
        # payload = json.loads(request.body)
        # event_type = payload.get('event')
        # transaction_id = payload['data']['object']['id'] # Example for Stripe     
        print(f"--- Received webhook from {gateway.upper()} ---")
        print(request.body)
        print("-------------------------------------------------")   
        
        # --- SIMULATED LOGIC ---
        # In a real app, you'd find the transaction by the gateway's ID.
        # For this simulation, we'll just grab the latest pending one for the user.
        try:
            # D1 DATABASE NOTE: This block should be atomic.
            with transaction.atomic():
                # Find the pending transaction
                # In a real app: transaction_to_update = Transaction.objects.get(gateway_txn_id=transaction_id)
                transaction_to_update = Transaction.objects.filter(status='PENDING').latest('created_at')
                
                # Update its status to 'COMPLETED'
                transaction_to_update.status = 'COMPLETED'
                transaction_to_update.save()
                
                # Add the purchased credits to the user's account
                user_credits = Credits.objects.get(user=transaction_to_update.user)
                user_credits.balance += transaction_to_update.credits_purchased
                user_credits.save()
                
            print(f"SUCCESS: Update transaction {transaction_to_update} to COMPLETE.")
            print(f"SUCCESS: Added {transaction_to_update.credits_purchased} credits to {transaction_to_update.user}")
        
        except Transaction.DoesNotExist:
            print("ERROR: Could not find a pending transaction to update.")
            return HttpResponseBadRequest("Transaction not found.")
        except Exception as e:
            print(f"ERROR: An error occurred processing webhook: {e}")
            return HttpResponse(status=500)
        
                # Return a 200 OK response to the gateway to acknowledge receipt.
        return HttpResponse(status=200)