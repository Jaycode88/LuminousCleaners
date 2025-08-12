from django.shortcuts import render
from contact.forms import ContactForm

def home(request):
    contact_form = ContactForm()
    return render(request, 'index.html', {'contact_form': contact_form})
