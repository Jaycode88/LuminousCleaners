from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
import requests

from .forms import ContactForm

def verify_recaptcha(token: str) -> bool:
    """Return True if Google reCAPTCHA verifies; False otherwise."""
    secret = getattr(settings, 'RECAPTCHA_SECRET_KEY', '')
    if not (secret and token):
        return False

    try:
        r = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={'secret': secret, 'response': token},
            timeout=6
        )
        data = r.json()
        return bool(data.get('success'))
    except requests.RequestException:
        return False


def too_many_recent_submissions(ip: str) -> bool:
    key = f"contact-throttle:{ip}"
    count = cache.get(key, 0)
    cache.set(key, count + 1, 60)  # 60s window
    return count > 5  # allow up to 5 per minute

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        recaptcha_token = request.POST.get('g-recaptcha-response')

        if form.is_valid():
            recaptcha_ok = True
            if recaptcha_token:
                recaptcha_ok = verify_recaptcha(recaptcha_token)

            if not recaptcha_ok:
                messages.error(request, "reCAPTCHA verification failed. Please try again.")
                return render(
                    request,
                    'contact/contact.html',
                    {'form': form, 'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY}
                )

            # Rate limiting before sending email
            ip = request.META.get('REMOTE_ADDR', '')
            if too_many_recent_submissions(ip):
                messages.error(request, "Too many submissions. Please wait a minute and try again.")
                return render(
                    request,
                    'contact/contact.html',
                    {'form': form, 'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY}
                )

            # Compose & send email (remember: you already popped hp fields)
            cleaned = form.cleaned_data
            cleaned.pop('hp_subject', None)
            cleaned.pop('form_start_ts', None)
            message = "\n".join([f"{k.replace('_',' ').title()}: {v}" for k, v in cleaned.items()])

            send_mail(
                "New Contact Form Submission",
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_FORM_EMAIL],
                fail_silently=False,
            )

            messages.success(request, "Thanks! Your message has been sent.")
            return redirect('home')

        # invalid form (honeypot/timing/etc)
        return render(
            request,
            'contact/contact.html',
            {'form': form, 'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY}
        )

    # GET
    form = ContactForm()
    return render(
        request,
        'contact/contact.html',
        {'form': form, 'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY}
    )
