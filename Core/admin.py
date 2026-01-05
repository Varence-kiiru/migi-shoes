from django.contrib import admin
from . import models

class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_email', 'contact_phone')
    fieldsets = (
        (None, {
            'fields': ('company_name', 'logo', 'favicon')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'business_hours', 'address', 'shipping_fee')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'linkedin_url'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(models.CompanySettings, CompanySettingsAdmin)
