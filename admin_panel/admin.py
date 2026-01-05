from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Sum, Count, F

from models_app.models import Customer, Order, OrderItem, Shoe, ShoeVariant

# https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#overriding-default-admin-site
class MigiShoesAdmin(admin.AdminSite):
    site_header = "Migi Shoes Admin Site"
    site_title = "Migi Shoes Admin Site"
    logout_template = 'admin/logout.html'
    
    def each_context(self, request):
        context = super().each_context(request)
        context['username'] = request.user.get_username
        return context
    
    def dashboard_view(self, request):
        request.current_app = self.name
        user = request.user

        # default main stats (used for superuser)
        total_customers = Customer.objects.count()
        orders_qs = Order.objects.all()
        total_orders = orders_qs.count()

        status_counts = orders_qs.values('status').annotate(count=Count('order_id'))
        status_summary = {}
        for entry in status_counts:
            name = entry['status'] or 'Unknown'
            cnt = entry['count']
            pct = (cnt / total_orders * 100) if total_orders else 0
            status_summary[name] = {'count': cnt, 'percent': round(pct, 1)}

        total_sales = orders_qs.aggregate(total=Sum('total_price'))['total'] or 0

        if user.is_superuser:
            template = "admin/dashboard.html"
            context = self.each_context(request)
            context.update({
                'total_customers': total_customers,
                'total_orders': total_orders,
                'status_summary': status_summary,
                'total_sales': total_sales,
                'most_sold': list(
                    OrderItem.objects.values().annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:10]
                ),
            })
            return TemplateResponse(request, template, context)

        # Inventory Manager
        if user.groups.filter(name='Inventory Manager').exists():
            low_stock_variants = (
                ShoeVariant.objects.filter(stock__lte=5)
                .select_related('shoe')
                .order_by('stock', 'shoe__name')
            )
            template = "admin/dashboard_inventory.html"
            context = self.each_context(request)
            context.update({
                'low_stock_variants': low_stock_variants,
            })
            return TemplateResponse(request, template, context)

        # Order Manager
        if user.groups.filter(name='Order Manager').exists():
            cancelled_orders = (
                Order.objects.filter(status='Cancelled')
                .select_related('customer__user')
                .prefetch_related('items')
                .order_by('-order_date')
            )
            template = "admin/dashboard_orders.html"
            context = self.each_context(request)
            context.update({
                'cancelled_orders': cancelled_orders,
            })
            return TemplateResponse(request, template, context)

        # Pricing Manager
        if user.groups.filter(name='Pricing Manager').exists():
            top_expensive = Shoe.objects.order_by('-price')[:5]
            top_cheap = Shoe.objects.order_by('price')[:5]
            template = "admin/dashboard_pricing.html"
            context = self.each_context(request)
            context.update({
                'top_expensive': top_expensive,
                'top_cheap': top_cheap,
            })
            return TemplateResponse(request, template, context)

        # default dashboard
        template = "admin/index.html"
        context = self.each_context(request)
        context.update({
            'total_customers': total_customers,
            'total_orders': total_orders,
            'status_summary': status_summary,
            'total_sales': total_sales,
            'most_sold': list(
                OrderItem.objects.values().annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:10]
            ),
        })
        return TemplateResponse(request, template, context)
    
    def get_urls(self):
        urls = super().get_urls()

        #print(urls) # testing purposes
        url_patterns = [
            path("", self.admin_view(self.dashboard_view), name="dashboard"),
        ] 
        return url_patterns + urls
