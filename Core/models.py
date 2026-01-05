from django.db import models

# Create your models here.

class CompanySettings(models.Model):
    company_name = models.CharField(max_length=100, default='Migi Shoes', help_text='Name of the company.')
    logo = models.ImageField(upload_to='company/', blank=True, null=True, help_text='Company logo image.')
    favicon = models.ImageField(upload_to='company/', blank=True, null=True, help_text='Company favicon image.')
    contact_email = models.EmailField(blank=True, help_text='Primary contact email.')
    contact_phone = models.CharField(max_length=20, blank=True, help_text='Primary contact phone number.')
    business_hours = models.CharField(max_length=200, blank=True, help_text='Business hours (e.g., Monday - Friday, 9 AM - 6 PM EAT).')
    address = models.TextField(blank=True, help_text='Company address.')
    facebook_url = models.URLField(blank=True, help_text='Facebook page URL.')
    instagram_url = models.URLField(blank=True, help_text='Instagram profile URL.')
    twitter_url = models.URLField(blank=True, help_text='Twitter/X profile URL.')
    linkedin_url = models.URLField(blank=True, help_text='LinkedIn page URL.')
    shipping_fee = models.DecimalField(max_digits=8, decimal_places=2, default=150.00, help_text='Flat shipping fee for all orders.')

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'
