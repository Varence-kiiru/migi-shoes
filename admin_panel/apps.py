from django.contrib.admin.apps import AdminConfig

# https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#overriding-default-admin-site
class AdminPanelConfig(AdminConfig):
    default_site = 'admin_panel.admin.MigiShoesAdmin'
    
from django.apps import AppConfig

class AdminAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_panel'

    def ready(self):
        # ensure signals run on startup/migrations
        import admin_panel.signals
