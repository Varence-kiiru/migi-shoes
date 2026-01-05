"""
URL configuration for Migi_shoes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
#from admin_panel.admin import admin_site

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('admin/', admin_site.urls), #custom admin site
    path('',include('storefront.urls')),
    # path('home/',include('storefront.urls')),
    path('products/', include('products.urls'), name='products'),
    path('accounts/',include('accounts.urls')),
    path('accounts/',include('django.contrib.auth.urls')), #dummy acc for testing
    path('customer/', include('customer.urls')),
    #path('adminpanel/', include('adminpanel.urls')),
    path('cart/', include('cart.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    #to store and show uploaded pics, not for production
