from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

PROPERTY_TYPES = [
    ('flat', 'Flat'),
    ('house', 'House'),
    ('bungalow', 'Bungalow'),
    ('commercial_office', 'Commercial Office'),
]

SERVICES = [
    ('deep_cleaning', 'Deep Cleaning'),
    ('commercial_cleaning', 'Commercial Cleaning'),
    ('domestic_cleaning', 'Domestic Cleaning'),
    ('appliance_cleaning', 'Appliance Cleaning'),
    ('steam_cleaning', 'Steam Cleaning'),
]

PROPERTY_SIZES = [
    ('1_bedroom', '1 Bedroom'),
    ('2_bedroom', '2 Bedrooms'),
    ('3_bedroom', '3 Bedrooms'),
    ('4_plus', '4+ Bedrooms'),
]

FREQUENCIES = [
    ('one_off', 'One Off'),
    ('weekly', 'Weekly'),
    ('bi_weekly', 'Bi-Weekly'),
    ('monthly', 'Monthly'),
]

class ContactForm(forms.Form):
    # Visible fields
    full_name = forms.CharField(max_length=100, label='Full Name')
    email = forms.EmailField(label='Email Address')
    phone = forms.CharField(max_length=20, label='Phone Number')
    property_type = forms.ChoiceField(choices=PROPERTY_TYPES)
    service_required = forms.ChoiceField(choices=SERVICES)
    property_size = forms.ChoiceField(choices=PROPERTY_SIZES)
    frequency = forms.ChoiceField(choices=FREQUENCIES)
    postcode = forms.CharField(max_length=10, label='Postcode')
    additional_details = forms.CharField(widget=forms.Textarea, required=False)

    # Honeypot (ALWAYS PRESENT)
    hp_subject = forms.CharField(required=False, label="Leave this field empty")

    # Submission timing (optional anti-bot)
    form_start_ts = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_hp_subject(self):
        """If the honeypot has any value, treat as spam."""
        val = self.cleaned_data.get('hp_subject', '').strip()
        if val:
            raise ValidationError("Spam detected.")
        return val

    def clean(self):
        cleaned = super().clean()

        # Optional: timing check (reject if submitted too fast, e.g., < 3 seconds)
        ts = cleaned.get('form_start_ts')
        try:
            if ts:
                start = float(ts)
                elapsed = timezone.now().timestamp() - start
                if elapsed < 3:  # adjust if you like
                    raise ValidationError("Form submitted too quickly. Please try again.")
        except (ValueError, TypeError):
            pass

        return cleaned
