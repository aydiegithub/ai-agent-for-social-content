from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction

from .forms import ContentGenerationForm
from .models import ContentHistory
from apps.billing.models import Credits
from core.ai_engine import gemini_client # We still use our AI engine

class DashboardView(LoginRequiredMixin, View):
    """
    The main dashboard view, reverted to use the standard Django ORM.
    """
    template_name = 'dashboard/dashboard.html'
    form_class = ContentGenerationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        
        # Use the standard Django ORM to fetch data
        content_history = ContentHistory.objects.filter(user=request.user)
        user_credits, _ = Credits.objects.get_or_create(user=request.user)

        context = {
            'form': form,
            'content_history': content_history,
            'credits': user_credits.balance
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        
        if form.is_valid():
            cost = 1
            if form.cleaned_data.get('generate_image'):
                cost += 3

            user_credits = Credits.objects.get(user=request.user)
            if user_credits.balance < cost:
                messages.error(request, f"You don't have enough credits for this operation.")
                return redirect('dashboard:dashboard')

            prompt_data = form.cleaned_data
            prompt = self._build_prompt(prompt_data)
            
            try:
                # Use a database transaction for safety. If any step fails,
                # the entire operation is rolled back.
                with transaction.atomic():
                    # 1. Call the AI to generate content.
                    generated_text = gemini_client.generate_text(prompt)
                    
                    image_url = None
                    if prompt_data.get('generate_image'):
                        image_prompt = f"An image for: {prompt_data['title']} in the {prompt_data['niche']} niche."
                        image_url = gemini_client.generate_image(image_prompt) # This would upload to R2

                    # 2. Deduct credits from the user's account.
                    user_credits.balance -= cost
                    user_credits.save()

                    # 3. Save the generated content to the user's history.
                    ContentHistory.objects.create(
                        user=request.user,
                        title=prompt_data['title'],
                        input_params=prompt_data,
                        generated_text=generated_text,
                        generated_image_url=image_url
                    )

                messages.success(request, "Content generated successfully!")

            except Exception as e:
                messages.error(request, f"An error occurred during generation: {e}")

            return redirect('dashboard:dashboard')
        
        # Re-render the page with form errors if invalid
        content_history = ContentHistory.objects.filter(user=request.user)
        user_credits, _ = Credits.objects.get_or_create(user=request.user)
        context = {
            'form': form,
            'content_history': content_history,
            'credits': user_credits.balance
        }
        return render(request, self.template_name, context)

    def _build_prompt(self, data):
        """Helper method to construct a detailed prompt from form data."""
        prompt = f"Generate content with the following specifications:\n"
        prompt += f"- Title: {data['title']}\n"
        prompt += f"- Niche/Industry: {data['niche']}\n"
        if data.get('context'):
            prompt += f"- Context/Details: {data['context']}\n"
        if data.get('tags'):
            prompt += f"- Important Keywords/Tags: {data['tags']}\n"
        prompt += "\nPlease provide a comprehensive and well-structured piece of content."
        return prompt