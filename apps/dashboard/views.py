from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction

from .forms import ContentGenerationForm
from .models import ContentHistory
from apps.billing.models import Credits

# Import the real AI client, replacing the simulation functions
from core.ai_engine import gemini_client

TEXT_GENERATION_COST = 1
IMAGE_GENERATION_COST = 3

class DashboardView(LoginRequiredMixin, View):
    """
    The main dashboard view for content generation and history.
    """
    template_name = 'dashboard/dashboard.html'
    form_class = ContentGenerationForm

    def get(self, request, *args, **kwargs):
        """Handles GET requests, displaying the form and user's content history."""
        form = self.form_class()
        
        content_history = ContentHistory.objects.filter(user=request.user)
        user_credits, _ = Credits.objects.get_or_create(user=request.user)

        context = {
            'form': form,
            'content_history': content_history,
            'credits': user_credits.balance
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Handles POST requests, processing the form to generate content."""
        form = self.form_class(request.POST)
        
        if form.is_valid():
            cost = TEXT_GENERATION_COST
            if form.cleaned_data.get('generate_image'):
                cost += IMAGE_GENERATION_COST

            user_credits = Credits.objects.get(user=request.user)
            if user_credits.balance < cost:
                messages.error(request, f"You don't have enough credits for this operation. This requires {cost} credits, but you only have {user_credits.balance}.")
                return redirect('dashboard:dashboard')

            prompt_data = form.cleaned_data
            prompt = self._build_prompt(prompt_data)
            
            try:
                with transaction.atomic():
                    # Call the REAL Gemini client to generate content
                    generated_text = gemini_client.generate_text(prompt)
                    
                    image_url = None
                    if prompt_data.get('generate_image'):
                        image_prompt = f"An image representing: {prompt_data['title']} in the {prompt_data['niche']} niche."
                        # Call the REAL Gemini client to generate an image
                        image_url = gemini_client.generate_image(image_prompt)

                    user_credits.balance -= cost
                    user_credits.save()

                    ContentHistory.objects.create(
                        user=request.user,
                        title=prompt_data['title'],
                        input_params=prompt_data,
                        generated_text=generated_text,
                        generated_image_url=image_url
                    )

                messages.success(request, "Content generated successfully!")

            except Exception as e:
                # Catch exceptions from our GeminiClient or other errors
                # and display a friendly message to the user.
                messages.error(request, f"An error occurred: {e}")

            return redirect('dashboard:dashboard')
        
        # If form is not valid, re-render the page with errors.
        content_history = ContentHistory.objects.filter(user=request.user)
        user_credits, _ = Credits.objects.get_or_create(user=request.user)
        context = {
            'form': form,
            'content_history': content_history,
            'credits': user_credits.balance
        }
        return render(request, self.template_name, context)

    def _build_prompt(self, data):
        """A helper method to construct a detailed prompt from form data."""
        prompt = f"Generate content with the following specifications:\n"
        prompt += f"- Title: {data['title']}\n"
        prompt += f"- Niche/Industry: {data['niche']}\n"
        
        if data.get('tone'):
            prompt += f"- Tone of Voice: {data['tone']}\n"
            
        if data.get('context'):
            prompt += f"- Context/Details to include: {data['context']}\n"
            
        if data.get('tags'):
            prompt += f"- Important Keywords/Tags: {data['tags']}\n"
            
        prompt += "\nPlease provide a comprehensive and well-structured piece of content based on these requirements."
        return prompt