from django.contrib import admin
from django.forms import Textarea, ModelForm
from django.db import models as dj_models
from models_app import models

class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 1

class ShoeImageInline(admin.TabularInline):
    model = models.ShoeImage
    extra = 1
    readonly_fields = ()
    fields = ('image', 'alt_text')

class ShoeVariantInline(admin.TabularInline):
    model = models.ShoeVariant
    extra = 1
    fields = ('color', 'size_system', 'size', 'stock_management', 'in_stock', 'stock', 'sku')

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if request.user.has_perm('models_app.change_stock_only') and not request.user.is_superuser:
            # allow editing only stock
            for f in ('color', 'size', 'sku'):
                if f not in readonly:
                    readonly.append(f)
        return readonly
    
class ShoeAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'gender', 'price')
    list_filter = ('brand', 'category', 'gender')
    search_fields = ('name', 'description', 'brand__name', 'variants__sku')
    inlines = [ShoeImageInline, ShoeVariantInline]
    autocomplete_fields = ('brand',)
    save_on_top = True

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))

        # Only restrict fields if user has price-only permission AND is not a superuser
        if request.user.has_perm('models_app.change_price_only') and not request.user.is_superuser:  # type: ignore[attr-defined]
            # explicitly mark other model fields as readonly for this user
            other_fields = ['name', 'brand', 'category', 'gender', 'description', 'discount']
            for f in other_fields:
                if f not in readonly_fields and f not in ('price', 'discount'):
                    readonly_fields.append(f)

        return readonly_fields

class CartItemInline(admin.TabularInline):
    model = models.CartItem
    extra = 0
    raw_id_fields = ('variant',)

class WishlistItemInline(admin.TabularInline):
    model = models.WishlistItem
    extra = 0
    raw_id_fields = ('shoe',)

class NotificationInline(admin.TabularInline):
    model = models.Notification
    extra = 0
    raw_id_fields = ('related_order',)
    fields = ('message', 'is_read', 'created_at', 'related_order')
    readonly_fields = ('created_at',)
    formfield_overrides = {
        dj_models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 40})},
    }


class PaymentMethodInline(admin.StackedInline):
    model = models.PaymentMethod
    extra = 0
    fields = ('payment_type', 'title', 'card_type', 'card_num', 'exp_date', 'holder_name', 'mpesa_phone', 'is_default')


class AddressInline(admin.StackedInline):
    model = models.Address
    extra = 0
    fields = ('title', 'first_name', 'last_name', 'street', 'city', 'zip_code', 'is_default')

class ShoeVariantAdmin(admin.ModelAdmin):
    list_display = ('variant_id', 'shoe', 'color', 'size', 'stock', 'sku')
    list_filter = ('shoe', 'color', 'size')
    search_fields = ('sku', 'shoe__name')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        # If user has special change_stock permission and is not superuser, allow editing only 'stock'
        if request.user.has_perm('models_app.change_stock_only') and not request.user.is_superuser:  # type: ignore[attr-defined]
            for f in ('shoe', 'color', 'size', 'sku'):
                if f not in readonly_fields:
                    readonly_fields.append(f)
        return readonly_fields


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)
    ordering = ('name',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'order_date', 'status', 'total_price')
    list_filter = ('status', 'order_date')
    search_fields = ('customer__user__username', 'id')
    inlines = [OrderItemInline]
    raw_id_fields = ('customer',)
    readonly_fields = ('subtotal',)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'get_product_name', 'quantity', 'price')
    search_fields = ('order__id', 'variant__shoe__name')
    raw_id_fields = ('order',)

    def get_product_name(self, obj):
        return obj.variant.shoe.name if obj.variant and obj.variant.shoe else 'Unknown'
    get_product_name.short_description = 'Product'

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'message', 'is_read', 'created_at', 'related_order')
    list_filter = ('is_read', 'created_at')
    search_fields = ('customer__user__username', 'message')
    raw_id_fields = ('customer', 'related_order')
    formfield_overrides = {
        dj_models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})},
    }


class PaymentMethodAdminForm(ModelForm):
    class Meta:
        model = models.PaymentMethod
        fields = '__all__'

    class Media:
        js = ('models_app/admin/js/payment_method_toggle.js',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for field grouping
        self.fields['card_num'].widget.attrs.update({'class': 'card-field'})
        self.fields['exp_date'].widget.attrs.update({'class': 'card-field'})
        self.fields['card_type'].widget.attrs.update({'class': 'card-field'})
        self.fields['holder_name'].widget.attrs.update({'class': 'card-field'})
        self.fields['mpesa_phone'].widget.attrs.update({'class': 'mpesa-field'})


class PaymentMethodAdmin(admin.ModelAdmin):
    form = PaymentMethodAdminForm
    list_display = ('card_id', 'title', 'customer', 'payment_type', 'card_type', 'holder_name', 'is_default')
    list_filter = ('payment_type', 'card_type', 'is_default')
    search_fields = ('customer__user__username', 'holder_name', 'card_num', 'mpesa_phone')
    raw_id_fields = ('customer',)
    actions = ('make_selected_default',)

    def save_model(self, request, obj, form, change):
        # If marking this payment method as default, unset others for the same customer
        super().save_model(request, obj, form, change)
        if obj.is_default and obj.customer:
            models.PaymentMethod.objects.filter(customer=obj.customer).exclude(pk=obj.pk).update(is_default=False)

    def make_selected_default(self, request, queryset):
        # Custom action to make only the first selected as default
        customers = {}
        for pm in queryset:
            if pm.customer:
                customers.setdefault(pm.customer.pk, []).append(pm)

        for cust_id, items in customers.items():
            # unset existing defaults
            models.PaymentMethod.objects.filter(customer_id=cust_id).update(is_default=False)
            # mark the first selected as default
            first = items[0]
            first.is_default = True
            first.save()

    make_selected_default.short_description = 'Set selected payment method as default (per customer)'

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating', 'date_added', 'order_item')
    search_fields = ('title', 'order_item__variant__shoe__name')


class AddressAdmin(admin.ModelAdmin):
    list_display = ('addr_id', 'title', 'customer', 'street', 'city', 'zip_code', 'is_default')
    list_filter = ('city', 'is_default')
    search_fields = ('customer__user__username', 'street', 'city', 'zip_code')
    raw_id_fields = ('customer',)
    actions = ('make_selected_default',)

    def make_selected_default(self, request, queryset):
        # Makes only the first selected address as default per customer
        customers = {}
        for addr in queryset:
            if addr.customer:
                customers.setdefault(addr.customer.pk, []).append(addr)

        for cust_id, items in customers.items():
            # unset existing defaults for that customer
            models.Address.objects.filter(customer_id=cust_id).update(is_default=False)
            # mark the first selected as default
            first = items[0]
            first.is_default = True
            first.save()

    make_selected_default.short_description = 'Set selected address as default (per customer)'
    
class SiteAdminAdmin(admin.ModelAdmin):
    list_display = ('admin_id', 'user', 'role')
    raw_id_fields = ('user',)

class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('customer', 'shoe', 'date_added')
    search_fields = ('customer__user__username', 'shoe__name')
    raw_id_fields = ('customer', 'shoe')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('customer', 'variant', 'quantity')
    search_fields = ('customer__user__username', 'variant__sku')
    raw_id_fields = ('customer', 'variant')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'mobile', 'theme_preference')
    search_fields = ('user__username', 'user__email', 'phone')
    raw_id_fields = ('user',)
    inlines = [CartItemInline, WishlistItemInline, NotificationInline, PaymentMethodInline, AddressInline]


admin.site.register(models.Shoe, ShoeAdmin)
admin.site.register(models.ShoeImage)
admin.site.register(models.ShoeVariant, ShoeVariantAdmin)
admin.site.register(models.Brand, BrandAdmin)
admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderItem, OrderItemAdmin)
admin.site.register(models.Notification, NotificationAdmin)
admin.site.register(models.Review, ReviewAdmin)
admin.site.register(models.Admin, SiteAdminAdmin)
admin.site.register(models.WishlistItem, WishlistItemAdmin)
admin.site.register(models.CartItem, CartItemAdmin)
admin.site.register(models.PaymentMethod, PaymentMethodAdmin)
admin.site.register(models.Address, AddressAdmin)
