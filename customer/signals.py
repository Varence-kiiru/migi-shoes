from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from models_app.models import Customer

@receiver(post_save, sender=User)
def create_customer_profile(sender, **kwargs):
    # Automatically create a Customer when a User is created
    # Create UserProfile object if User object is new and not loaded from fixture
    if kwargs['created'] and not kwargs['raw']:
        user = kwargs['instance']
        if not (user.is_staff or user.is_superuser): #Exclude admin users
            Customer.objects.get_or_create(user=user)
    # Double check UserProfile doesn't exist already
    # (admin might create it before the signal fires)
