from django.shortcuts import render, redirect
from django.contrib import messages
from models_app.models import Shoe
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views import generic
from models_app import models
#for email sending
from django.core.mail import send_mail
from django.conf import settings
###       home page
def home(request):
    context={
        'active_class':'home'
    }
    return render(request,'storefront/home.html',context)

###       about page
def about(request):
    context={
        'active_class':'aboutus'
    }
    return render(request,"storefront/about.html",context)

###       contact page    ###
def contact(request):

    if request.method == 'POST':

        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('telnum')
        message = request.POST.get('message')

        # Required fields validation (phone is optional)
        if not fname or not fname.strip():
            messages.error(request, "First name is required.", extra_tags='contactSuccess')
            return render(request, 'storefront/contact.html', {
                'fname': fname,
                'lname': lname,
                'email': email,
                'telnum': phone,
                'message': message,
            })
        if len(fname) > 50:
            messages.error(request, "First name must be 50 characters or fewer.", extra_tags='contactSuccess')
            return render(request, 'storefront/contact.html', {
                'fname': fname,
                'lname': lname,
                'email': email,
                'telnum': phone,
                'message': message,
            })

        if not lname or not lname.strip():
            messages.error(request, "Last name is required.", extra_tags='contactSuccess')
            return render(request, 'storefront/contact.html', {
                'fname': fname,
                'lname': lname,
                'email': email,
                'telnum': phone,
                'message': message,
            })
        if len(lname) > 50:
            messages.error(request, "Last name must be 50 characters or fewer.", extra_tags='contactSuccess')
            return render(request, 'storefront/contact.html', {
                'fname': fname,
                'lname': lname,
                'email': email,
                'telnum': phone,
                'message': message,
            })

        if not email or not email.strip():
            messages.error(request, "Email is required.", extra_tags='contactSuccess')
            return render(request, 'storefront/contact.html', {
                'fname': fname,
                'lname': lname,
                'email': email,
                'telnum': phone,
                'message': message,
            })

        if not message or not message.strip():
            messages.error(request, "Message is required.", extra_tags='contactSuccess')
            return render(request, 'storefront/contact.html', {
                'fname': fname,
                'lname': lname,
                'email': email,
                'telnum': phone,
                'message': message,
            })

        # Email validation using built-in email validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.",extra_tags='contactSuccess')
            #re-render with existing data

            return render(request, 'storefront/contact.html', {
                'fname': fname,
                'lname': lname,
                'email': email,
                'telnum': phone,
                'message': message,
            })
        
        #### email validation using regex for email domains ###
        common_email_pattern = re.compile(r'^[A-Za-z0-9._%+-]+@(?:gmail\.com|yahoo\.com|outlook\.com|hotmail\.com|icloud\.com|protonmail\.com)$')
        if not common_email_pattern.match(email):
            messages.error(request, "Invalid email domain. Please use Gmail, Yahoo, Outlook, Hotmail, iCloud, or ProtonMail.", extra_tags='contactSuccess')
            return render(request, 'storefront/contact.html', {
                'fname': fname,
                'lname': lname,
                'email': email,
                'telnum': phone,
                'message': message,
            })


        #Phone validation with regex
        # Phone is optional; if provided, validate format +230######## (8 digits)
        phone_pattern = re.compile(r'^\+230\d{8}$')
        if phone:
            if not phone_pattern.match(phone):
                messages.error(request, "Invalid phone number. Use format +23012345678 (exactly 8 digits after +230).", extra_tags='contactSuccess')
                # re-render with existing data
                return render(request, 'storefront/contact.html', {
                    'fname': fname,
                    'lname': lname,
                    'email': email,
                    'telnum': phone,
                    'message': message,
                })


        # Build email content
        subject = f"New Contact Us Message from {fname} {lname}"
        body = f"""
        You have received a new message from the Contact Us form:

        Name: {fname} {lname}
        Email: {email}
        Phone Number: {phone}
        Message:
        {message}
        """

        # Send email
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,        # sender (your account)
            ['admin@olivian.co.ke'],       # recipient (your inbox)
            fail_silently=False,
        )

        # … process form and send email …
        messages.success(request, f"Thank you {fname}, your message has been sent!", extra_tags='contactSuccess')
        return redirect('storefront:contact')
    return render(request, 'storefront/contact.html')


def categories(request):
    #Lists a few samples from each category
    categories = Shoe.CATEGORY_CHOICES
    categories_list = []
    for code, label in categories.items():
        samples = list(Shoe.objects.filter(category=code)[:4])
        categories_list.append({
            'code': code,
            'label': label,
            'shoes': samples,
        })

    context = {
        'categories_list': categories_list,
        'active_class': 'categories',
    }
    return render(request, 'storefront/categories.html', context)

class BrandListView(generic.ListView):
    model = models.Brand
    template_name = 'storefront/brand_list.html'
    context_object_name = 'brands'

    def get_queryset(self):
        return super().get_queryset().order_by('name')

from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect

@require_POST
def toggle_theme(request):
    """Toggle the site theme between 'light' and 'dark' using a cookie."""

    next_url = request.META.get('HTTP_REFERER') or '/'
    current = request.COOKIES.get('theme', 'light')
    new = 'dark' if current == 'light' else 'light'
    response = HttpResponseRedirect(next_url)
    # persist for 1 year
    response.set_cookie('theme', new, max_age=60 * 60 * 24 * 365, httponly=False)
    return response

###       privacy policy page
def privacy_policy(request):
    context = {
        'active_class': 'privacy'
    }
    return render(request, "storefront/privacy_policy.html", context)

###       terms of service page
def terms_of_service(request):
    context = {
        'active_class': 'terms'
    }
    return render(request, "storefront/terms_of_service.html", context)

###       FAQ page
def faq(request):
    context = {
        'active_class': 'faq'
    }
    return render(request, "storefront/faq.html", context)
