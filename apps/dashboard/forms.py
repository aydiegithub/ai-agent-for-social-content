from django import forms


class ContentGenerationForm(forms.Form):
    """
    A form for user to input the parameters for AI content generation
    """

    # Choices for the tone field to guide the user.
    TONE_CHOICES = [
        ('', 'Select a Tone (Optional)'),
        ('Formal', 'Formal'),
        ('Casual', 'Casual'),
        ('Humorous', 'Humorous'),
        ('Authoritative', 'Authoritative'),
        ('Inspirational', 'Inspirational'),
        ('Educational', 'Educational'),
        ('Serious', 'Serious'),
    ]

    title = forms.CharField(
        max_length=200,
        required=True,
        label="Content Title",
        help_text="The main headline or title for your content.",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Technology, Marketing, Health, Space'})
    )
    
    niche = forms.CharField(
        max_length=100,
        required=True,
        label="Niche / Industry",
        help_text="The target industry for this content.",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Technology, Marketing, Health'})
    )

    context = forms.CharField(
        required=False,
        label="Context or Background",
        help_text="Provide any relevant background, key points, or specific details to include.",
        widget=forms.Textarea(attrs={
            'placeholder': 'e.g., Focus on solar and wind power, mention recent policy changes...',
            'rows': 4
        })
    )

    tone = forms.ChoiceField(
        choices=TONE_CHOICES,
        required=False,
        label="Tone of Voice",
        help_text="Choose the desired writing style."
    )
    
    tags = forms.CharField(
        required=False,
        label="Keywords or Tags",
        help_text="Comma-separated keywords for categorization.",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., solar power, green tech, sustainability'})
    )
    
    generate_image = forms.BooleanField(
        required=False,
        label="Generate a matching image (costs 3 credits)",
        help_text="Create a unique AI-generated image based on your content title and niche."
    )