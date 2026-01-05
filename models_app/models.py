from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
#from django.db import transaction

# Create your models here.

class Shoe(models.Model):
    GENDER_CHOICES = {
        'M': 'Men',
        'W': 'Women',
        'U': 'Unisex',
        'K': 'Kids',
    }
    
    CATEGORY_CHOICES = {
        'running': 'Running',
        'casual': 'Casual',
        'sneakers': 'Sneakers',
        'formal': 'Formal',
        'boots': 'Boots',
        'sandals': 'Sandals',
    }
    
    shoe_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=2000, help_text='Detailed description of the shoe.')
    price = models.DecimalField(max_digits=8, decimal_places=2, help_text='Price in store currency (e.g. 49.99).')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, help_text='Product category (Running, Casual, etc.).')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, help_text='Target audience (Men/Women/Unisex/Kids).')
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, blank=True, related_name='shoes', help_text='Brand associated with this shoe (optional).')
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='Raw discount amount.')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:shoe_details', args=[self.shoe_id])

    def is_available(self):
        """Check if the shoe has any available variants (based on in_stock checkbox)"""
        return any(variant.is_available for variant in self.variants.all())  # type: ignore[attr-defined]

    def total_stock(self):
        # variants is a related_name from ShoeVariant; keep dynamic access at runtime
        return sum(variant.stock for variant in self.variants.all())  # type: ignore[attr-defined]
    
    @property
    def original_price(self):
        if self.discount > 0:
            return self.price + self.discount
        return self.price

    class Meta:
        permissions = [
            ('change_price_only', 'Can change shoe price (price-only)'),
        ]
    
class ShoeImage(models.Model):
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='images', help_text='Shoe this image belongs to.')
    image = models.ImageField(upload_to='shoe_images/', help_text='Image file for the shoe.')
    alt_text = models.CharField(max_length=255, blank=True, help_text='Alt text for accessibility (optional).')

    def __str__(self):
        return f'Image for {self.shoe.name}'

class ShoeVariant(models.Model):
    SIZE_SYSTEM_CHOICES = [
        ('EU', 'European (EU)'),
        ('US', 'United States (US)'),
    ]

    STOCK_MANAGEMENT_CHOICES = [
        ('boolean', 'In Stock Checkbox'),
        ('quantity', 'Stock Quantity'),
    ]

    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='variants', help_text='Parent shoe for this variant.')
    color = models.CharField(max_length=50, help_text='Color or pattern of this variant.')
    size_system = models.CharField(max_length=2, choices=SIZE_SYSTEM_CHOICES, default='EU', help_text='Size system (EU or US).')
    size = models.DecimalField(max_digits=4, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(60)], help_text='Shoe size (EU: 35-49, US: 4-15).')
    stock_management = models.CharField(max_length=10, choices=STOCK_MANAGEMENT_CHOICES, default='boolean', help_text='Stock management method.')
    in_stock = models.BooleanField(default=True, help_text='Is this variant currently in stock? (for boolean management)')
    stock = models.IntegerField(validators=[MinValueValidator(0)], default=0, help_text='Units available in stock (for quantity management).')
    sku = models.CharField(max_length=100, blank=True, help_text='SKU identifier (auto-generated if blank).')
    variant_id = models.AutoField(primary_key=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f'{self.shoe.shoe_id}-{self.color[:3].upper()}-{self.size_system}{self.size}'
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        """Check if variant is available (in_stock checkbox takes precedence)"""
        return self.in_stock

    def __str__(self):
        return f'{self.shoe.name} - {self.color} - {self.size_system} {self.size}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['shoe', 'color', 'size_system', 'size'], name='unique_shoe_color_size_system_size')
        ]
        permissions = [
            ('change_stock_only', 'Can change variant stock (stock-only)'),
        ]
    
    
class Brand(models.Model):
    name = models.CharField(max_length=100, help_text='Brand name.')
    description = models.TextField(help_text='Short description about the brand.')
    website = models.URLField(blank=True, help_text='Official brand website URL (optional).')
    brand_id = models.AutoField(primary_key=True)
    logo = models.ImageField(upload_to='brand_logos/', null=True, blank=True, help_text='Brand logo image (optional).')
    
    def __str__(self):
        return self.name
     
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', help_text='Linked Django user account.')
    customer_id = models.AutoField(primary_key=True)
    date_of_birth = models.DateField(null=True, blank=True, help_text='Date of birth (optional).')
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        blank=True,
        help_text='Customer gender (optional).'
    )
    phone = models.CharField(max_length=15, blank=False, default="", help_text='Primary phone number.')
    mobile = models.CharField(max_length=15, blank=True, default="", help_text='Mobile/secondary phone (optional).')
    theme_preference = models.CharField(
        max_length=10,
        choices=[("light", "Light"), ("dark", "Dark")],
        default="light",
        help_text='Preferred UI theme.'
    )
    wishlist_items = models.ManyToManyField(Shoe, through='WishlistItem', related_name='wishlisted_by_customers', help_text='Shoes added to customer wishlist.')

    def __str__(self):
        return self.user.username
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

class PaymentMethod(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('card', 'Card'),
        ('mpesa', 'M-Pesa'),
    ]

    CARD_TYPE_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]

    card_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, help_text='Optional label for this payment method.')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, related_name='payment_methods', null=True, blank=True, help_text='Owning customer (optional).')
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, default='card', help_text='Type of payment method.')
    # Card fields
    card_num = models.CharField(max_length=19, blank=True, help_text='Card number digits only (13-19 chars).')
    exp_date = models.DateField(null=True, blank=True, help_text='Card expiration date.')
    card_type = models.CharField(max_length=10, choices=CARD_TYPE_CHOICES, blank=True, help_text='Debit or Credit.')
    holder_name = models.CharField(max_length=100, blank=True, help_text='Name on the card.')
    # M-Pesa fields
    mpesa_phone = models.CharField(max_length=15, blank=True, help_text='M-Pesa registered phone number.')
    is_default = models.BooleanField(default=False, help_text='Set as default payment method for the customer.')

    def clean(self):
        errors = {}

        if self.payment_type == 'card':
            if not self.card_num:
                errors['card_num'] = 'Card number is required for card payments.'
            elif not self.card_num.isdigit() or not (13 <= len(self.card_num) <= 19):
                errors['card_num'] = 'Card number must be 13 to 19 digits (numbers only).'

            if not self.exp_date:
                errors['exp_date'] = 'Expiration date is required for card payments.'
            elif self.exp_date and self.exp_date <= timezone.now().date():
                errors['exp_date'] = 'Expiration date must be in the future.'

            if not self.card_type:
                errors['card_type'] = 'Card type is required for card payments.'

            if not self.holder_name:
                errors['holder_name'] = 'Card holder name is required for card payments.'

        elif self.payment_type == 'mpesa':
            if not self.mpesa_phone:
                errors['mpesa_phone'] = 'M-Pesa phone number is required for M-Pesa payments.'
            elif not self.mpesa_phone.isdigit() or len(self.mpesa_phone) < 9:
                errors['mpesa_phone'] = 'M-Pesa phone number must be at least 9 digits.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        # If no title is provided, set a default title
        if not self.title or not self.title.strip():
            if self.payment_type == 'card':
                last4 = self.card_num[-4:] if self.card_num else ''
                self.title = f"{self.get_card_type_display()} ****{last4}"  # type: ignore[attr-defined]
            elif self.payment_type == 'mpesa':
                last4 = self.mpesa_phone[-4:] if self.mpesa_phone else ''
                self.title = f"M-Pesa ****{last4}"

        # If  newly created payment method and no other methods,
        # make it the default automatically.
        is_new = self.pk is None #Not created yet
        if is_new and self.customer:
            has_other = PaymentMethod.objects.filter(customer=self.customer).exists()
            if not has_other:
                self.is_default = True

        super().save(*args, **kwargs)
        if self.is_default and self.customer:
            # Unset other defaults for this customer
            PaymentMethod.objects.filter(customer=self.customer).exclude(pk=self.pk).update(is_default=False)

    @property
    def masked(self):
        """Return masked payment identifier string."""
        if self.payment_type == 'card':
            last4 = self.card_num[-4:] if self.card_num else '----'
            return f'****{last4}'
        elif self.payment_type == 'mpesa':
            last4 = self.mpesa_phone[-4:] if self.mpesa_phone else '----'
            return f'****{last4}'
        return '----'

    def __str__(self):
        if self.payment_type == 'card':
            return f'PM {self.card_id} - {self.masked} ({self.holder_name})'
        elif self.payment_type == 'mpesa':
            return f'PM {self.card_id} - M-Pesa {self.masked}'
        return f'PM {self.card_id}'

class Address(models.Model):
    addr_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, help_text='Optional address label (Home, Work).')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, related_name='addresses', null=True, blank=True, help_text='Customer this address belongs to (optional).')
    street = models.CharField(max_length=255, help_text='Street address line.')
    city = models.CharField(max_length=100, help_text='City.')
    zip_code = models.CharField(max_length=5, help_text='ZIP/postal code (5 chars).')
    first_name = models.CharField(max_length=50, help_text='Recipient first name.')
    last_name = models.CharField(max_length=50, help_text='Recipient last name.')
    is_default = models.BooleanField(default=False, help_text='Mark as default address for the customer.')

    class Meta:
        verbose_name_plural = 'Addresses'

    def save(self, *args, **kwargs):
        # If no title is provided, set a default title safely
        if not self.title or not self.title.strip():
            self.title = f"{self.first_name.strip()}-{self.street.strip()[:10]}-{self.city.strip()}"

        super().save(*args, **kwargs)
        if self.is_default and self.customer:
            Address.objects.filter(customer=self.customer).exclude(pk=self.pk).update(is_default=False)

    def __str__(self):
        cust = self.customer.user.username if self.customer else 'Unknown'

        return f'Address {self.addr_id} - {self.street}, {self.city} ({cust})'

class Coupon(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    promo_code = models.CharField(max_length=50, unique=True, help_text='Code customers enter to receive the discount.')
    description = models.TextField(blank=True, help_text='Optional description for the coupon.')
    percent_off = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text='Discount percentage 0-100.')
    is_active = models.BooleanField(default=True, help_text='Whether the coupon is active.')
    exp_date = models.DateTimeField(null=True, blank=True, help_text='Optional expiration date/time.')

    def is_valid(self) -> bool:
        if not self.is_active:
            return False
        if self.exp_date and self.exp_date < timezone.now():
            return False
        return True

    def __str__(self):
        return f'Coupon {self.promo_code} - {self.percent_off}%'

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', help_text='Customer who placed the order.')
    order_date = models.DateField(auto_now_add=True, help_text='Date order was created.')
    delivery_date = models.DateTimeField(null=True, blank=True, help_text='Estimated or actual delivery date/time.')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text='Order status.')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='Total charged for the order (includes shipping/discounts).') #to replace
    shipping_address = models.ForeignKey('Address', null=True, blank=True, on_delete=models.SET_NULL, related_name='orders_with_shipping', help_text='Shipping address used for this order.')
    billing_address = models.ForeignKey('Address', null=True, blank=True, on_delete=models.SET_NULL, related_name='orders_with_billing', help_text='Billing address used for this order.')
    payment_method = models.ForeignKey('PaymentMethod', null=True, blank=True, on_delete=models.SET_NULL, related_name='orders', help_text='Payment method used (optional).')
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=100.00, help_text='Applied shipping cost.')
    subtotal = models.DecimalField(max_digits=8, decimal_places=2, blank=True, default=0.00, help_text='Sum of item subtotals before shipping/discounts.')
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text='Total discount applied to the order.')
    
    def update_subtotal(self):
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.save(update_fields=['subtotal'])

    @property
    def payment_method_label(self):
        pm = self.payment_method
        if pm is None:
            return 'Cash on delivery'
        return pm.title if pm.title else getattr(pm, 'masked', str(pm))

    def get_absolute_url(self):
        return reverse('customer:order_details', args=[self.order_id])

    def __str__(self):
        return f"Order #{self.order_id} - {self.customer.user.username}"
        
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', help_text='Order this item belongs to.')
    quantity = models.PositiveIntegerField(default=1, help_text='Quantity purchased.')
    price = models.DecimalField(max_digits=8, decimal_places=2, help_text='Unit price at time of purchase.')
    variant = models.ForeignKey('ShoeVariant', on_delete=models.CASCADE, related_name='order_items', help_text='Specific shoe variant ordered.')

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"Order #{self.order.order_id}: {self.variant.shoe.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.variant.shoe.price

        super().save(*args, **kwargs)
        self.order.update_subtotal()

class Notification(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="notifications", help_text='Recipient customer for this notification.')
    message = models.TextField(help_text='Notification text content.')
    is_read = models.BooleanField(default=False, help_text='Whether the notification has been read.')
    created_at = models.DateTimeField(auto_now_add=True, help_text='When the notification was created.')
    related_order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications", help_text='Optional related order.'
    )

    def __str__(self):
        return f"Notification for {self.customer.user.username}: {self.message[:10]}..."

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, help_text='Short review title.')
    comment = models.TextField(help_text='Full review comment.')
    date_added = models.DateTimeField(auto_now_add=True, help_text='When the review was submitted.')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='Rating from 1 to 5.')
    order_item = models.ForeignKey('OrderItem', on_delete=models.CASCADE, related_name='review', help_text='Order item this review refers to.')
    
    def __str__(self):
        return self.title

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_profile',
        null=True,
        blank=True
    )
    role = models.CharField(max_length=100, help_text='Admin role/title.')
    description = models.TextField(blank=True, help_text='Optional admin description.')

    def __str__(self):
        return f'Admin {self.admin_id} - {self.role}'

class WishlistItem(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, help_text='Customer who added the item to wishlist.')
    shoe = models.ForeignKey('Shoe', on_delete=models.CASCADE, related_name='wishlisted_by', help_text='Shoe added to wishlist.')
    date_added = models.DateTimeField(auto_now_add=True, help_text='When the wishlist item was added.')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['customer', 'shoe'], name='unique_wishlist_customer_shoe')
        ]

    def __str__(self):
        return f'WishlistItem {self.shoe} for {self.customer}'

class CartItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cart_items', help_text='Owner of this cart item.')
    variant = models.ForeignKey(ShoeVariant, on_delete=models.CASCADE, help_text='Variant (size/color) in the cart.')
    quantity = models.PositiveIntegerField(default=1, help_text='Quantity of the variant.')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['customer', 'variant'], name='unique_cart_customer_variant')
        ]

    @property
    def total_price(self):
        # Price is already discounted in the Shoe model
        return self.variant.shoe.price * self.quantity

    def __str__(self):
        return f"{self.variant} (x{self.quantity})"
