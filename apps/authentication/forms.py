from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

# --- Choices for our new dropdown fields ---
# A short list of countries for the dropdown
COUNTRY_CHOICES = [
    ('', 'Select a Country'),
    ('AF', 'Afghanistan'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AS', 'American Samoa'),
    ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AQ', 'Antarctica'),
    ('AG', 'Antigua and Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'), ('AW', 'Aruba'),
    ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BS', 'Bahamas'),
    ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'),
    ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermuda'),
    ('BT', 'Bhutan'), ('BO', 'Bolivia'), ('BA', 'Bosnia and Herzegovina'), ('BW', 'Botswana'),
    ('BR', 'Brazil'), ('IO', 'British Indian Ocean Territory'), ('BN', 'Brunei Darussalam'),
    ('BG', 'Bulgaria'), ('BF', 'Burkina Faso'), ('BI', 'Burundi'), ('CV', 'Cabo Verde'),
    ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('KY', 'Cayman Islands'),
    ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'),
    ('CX', 'Christmas Island'), ('CC', 'Cocos (Keeling) Islands'), ('CO', 'Colombia'),
    ('KM', 'Comoros'), ('CG', 'Congo'), ('CD', 'Congo, Democratic Republic of the'),
    ('CK', 'Cook Islands'), ('CR', 'Costa Rica'), ('CI', "Côte d'Ivoire"),
    ('HR', 'Croatia'), ('CU', 'Cuba'), ('CW', 'Curaçao'), ('CY', 'Cyprus'),
    ('CZ', 'Czechia'), ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'),
    ('DO', 'Dominican Republic'), ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'),
    ('GQ', 'Equatorial Guinea'), ('ER', 'Eritrea'), ('EE', 'Estonia'), ('SZ', 'Eswatini'),
    ('ET', 'Ethiopia'), ('FK', 'Falkland Islands'), ('FO', 'Faroe Islands'),
    ('FJ', 'Fiji'), ('FI', 'Finland'), ('FR', 'France'), ('GF', 'French Guiana'),
    ('PF', 'French Polynesia'), ('TF', 'French Southern Territories'), ('GA', 'Gabon'),
    ('GM', 'Gambia'), ('GE', 'Georgia'), ('DE', 'Germany'), ('GH', 'Ghana'),
    ('GI', 'Gibraltar'), ('GR', 'Greece'), ('GL', 'Greenland'), ('GD', 'Grenada'),
    ('GP', 'Guadeloupe'), ('GU', 'Guam'), ('GT', 'Guatemala'), ('GG', 'Guernsey'),
    ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HT', 'Haiti'),
    ('HM', 'Heard Island and McDonald Islands'), ('VA', 'Holy See'), ('HN', 'Honduras'),
    ('HK', 'Hong Kong'), ('HU', 'Hungary'), ('IS', 'Iceland'), ('IN', 'India'),
    ('ID', 'Indonesia'), ('IR', 'Iran'), ('IQ', 'Iraq'), ('IE', 'Ireland'),
    ('IM', 'Isle of Man'), ('IL', 'Israel'), ('IT', 'Italy'), ('JM', 'Jamaica'),
    ('JP', 'Japan'), ('JE', 'Jersey'), ('JO', 'Jordan'), ('KZ', 'Kazakhstan'),
    ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KP', 'Korea, North'), ('KR', 'Korea, South'),
    ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'), ('LA', 'Laos'), ('LV', 'Latvia'),
    ('LB', 'Lebanon'), ('LS', 'Lesotho'), ('LR', 'Liberia'), ('LY', 'Libya'),
    ('LI', 'Liechtenstein'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('MO', 'Macao'),
    ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'), ('MV', 'Maldives'),
    ('ML', 'Mali'), ('MT', 'Malta'), ('MH', 'Marshall Islands'), ('MQ', 'Martinique'),
    ('MR', 'Mauritania'), ('MU', 'Mauritius'), ('YT', 'Mayotte'), ('MX', 'Mexico'),
    ('FM', 'Micronesia'), ('MD', 'Moldova'), ('MC', 'Monaco'), ('MN', 'Mongolia'),
    ('ME', 'Montenegro'), ('MS', 'Montserrat'), ('MA', 'Morocco'), ('MZ', 'Mozambique'),
    ('MM', 'Myanmar'), ('NA', 'Namibia'), ('NR', 'Nauru'), ('NP', 'Nepal'),
    ('NL', 'Netherlands'), ('NC', 'New Caledonia'), ('NZ', 'New Zealand'),
    ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'), ('NU', 'Niue'),
    ('NF', 'Norfolk Island'), ('MK', 'North Macedonia'), ('MP', 'Northern Mariana Islands'),
    ('NO', 'Norway'), ('OM', 'Oman'), ('PK', 'Pakistan'), ('PW', 'Palau'),
    ('PS', 'Palestine'), ('PA', 'Panama'), ('PG', 'Papua New Guinea'), ('PY', 'Paraguay'),
    ('PE', 'Peru'), ('PH', 'Philippines'), ('PN', 'Pitcairn'), ('PL', 'Poland'),
    ('PT', 'Portugal'), ('PR', 'Puerto Rico'), ('QA', 'Qatar'), ('RE', 'Réunion'),
    ('RO', 'Romania'), ('RU', 'Russia'), ('RW', 'Rwanda'), ('BL', 'Saint Barthélemy'),
    ('SH', 'Saint Helena'), ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'),
    ('MF', 'Saint Martin'), ('PM', 'Saint Pierre and Miquelon'), ('VC', 'Saint Vincent and the Grenadines'),
    ('WS', 'Samoa'), ('SM', 'San Marino'), ('ST', 'Sao Tome and Principe'),
    ('SA', 'Saudi Arabia'), ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'),
    ('SL', 'Sierra Leone'), ('SG', 'Singapore'), ('SX', 'Sint Maarten'), ('SK', 'Slovakia'),
    ('SI', 'Slovenia'), ('SB', 'Solomon Islands'), ('SO', 'Somalia'), ('ZA', 'South Africa'),
    ('GS', 'South Georgia and the South Sandwich Islands'), ('SS', 'South Sudan'),
    ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('SD', 'Sudan'), ('SR', 'Suriname'),
    ('SJ', 'Svalbard and Jan Mayen'), ('SE', 'Sweden'), ('CH', 'Switzerland'),
    ('SY', 'Syria'), ('TW', 'Taiwan'), ('TJ', 'Tajikistan'), ('TZ', 'Tanzania'),
    ('TH', 'Thailand'), ('TL', 'Timor-Leste'), ('TG', 'Togo'), ('TK', 'Tokelau'),
    ('TO', 'Tonga'), ('TT', 'Trinidad and Tobago'), ('TN', 'Tunisia'), ('TR', 'Turkey'),
    ('TM', 'Turkmenistan'), ('TC', 'Turks and Caicos Islands'), ('TV', 'Tuvalu'),
    ('UG', 'Uganda'), ('UA', 'Ukraine'), ('AE', 'United Arab Emirates'),
    ('GB', 'United Kingdom'), ('US', 'United States'), ('UM', 'United States Minor Outlying Islands'),
    ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VU', 'Vanuatu'), ('VE', 'Venezuela'),
    ('VN', 'Vietnam'), ('VG', 'Virgin Islands, British'), ('VI', 'Virgin Islands, U.S.'),
    ('WF', 'Wallis and Futuna'), ('EH', 'Western Sahara'), ('YE', 'Yemen'),
    ('ZM', 'Zambia'), ('ZW', 'Zimbabwe'), ('OTHER', 'Other')
]

PROFESSION_CHOICES = [
    ('', 'Select a Profession'),
    ('developer', 'Software Developer'), ('designer', 'Designer'),
    ('manager', 'Product Manager'), ('marketer', 'Marketer'),
    ('student', 'Student'), ('business_owner', 'Business Owner'),
    ('other', 'Other')
]

HEAR_ABOUT_CHOICES = [
    ('', 'How did you hear about us?'),
    ('social_media', 'Social Media (X, LinkedIn, etc.)'),
    ('search_engine', 'Search Engine (Google, etc.)'),
    ('friend', 'From a Friend or Colleague'),
    ('advertisement', 'Advertisement'),
    ('other', 'Other')
]

INTERESTS_CHOICES = [
    ('technology', 'Technology'), ('marketing', 'Marketing'),
    ('business', 'Business'), ('design', 'Design'),
    ('health', 'Health & Wellness'), ('finance', 'Finance'),
    ('space', 'Space Exploration'), ('ai', 'Artificial Intelligence')
]


class CustomUserCreationForm(forms.ModelForm):
    # --- Core Fields (Required) ---
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    # --- Survey Fields (with new types and requirements) ---
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True  # Now required
    )
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        required=True  # Now required
    )
    how_did_you_hear_about_us = forms.ChoiceField(
        choices=HEAR_ABOUT_CHOICES,
        required=True, # Now required
        label="How did you hear about us?"
    )
    interests = forms.MultipleChoiceField(
        choices=INTERESTS_CHOICES,
        widget=forms.CheckboxSelectMultiple, # Renders as checkboxes
        required=False,
        label="What are your interests?"
    )
    
    # --- Optional Fields ---
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=False)
    profession = forms.ChoiceField(choices=PROFESSION_CHOICES, required=False)
    referral_code = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'email', 'password', 'confirm_password',
            'date_of_birth', 'country', 'how_did_you_hear_about_us',
            'interests', 'gender', 'profession', 'referral_code'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_classes = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
        
        for field_name, field in self.fields.items():
            # Apply styles to all fields except the interest checkboxes
            if field_name != 'interests':
                field.widget.attrs.update({'class': tailwind_classes})
            
            # Add placeholders
            placeholder = field.label if field.label else field_name.replace('_', ' ').title()
            field.widget.attrs.update({'placeholder': placeholder})

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        
        # The 'interests' field gives a list. We join it into a string to save.
        if 'interests' in self.cleaned_data:
            user.interests = ",".join(self.cleaned_data['interests'])
            
        if commit:
            user.save()
        return user

# ... (CustomLoginForm and OTPVerificationForm remain unchanged) ...
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Password'
    }))

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 text-center tracking-[1em] border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': '------'
        })
    )