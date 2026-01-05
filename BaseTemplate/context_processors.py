def theme(request):
    """Expose the current theme (from cookie) to templates.

    Returns 'dark' or 'light'. Default is 'light'.
    """
    theme = request.COOKIES.get('theme', 'light')
    return {
        'theme': theme
    }

def company_settings(request):
    """Expose company settings to all templates."""
    from Core.models import CompanySettings
    settings = CompanySettings.objects.first()
    if not settings:
        # Create default if none exists
        settings = CompanySettings.objects.create(
            company_name='Migi Shoes',
            contact_email='info@migishoes.com',
            contact_phone='+254715462406',
            business_hours='Monday - Friday, 9 AM - 6 PM EAT'
        )
    return {
        'company': settings
    }
