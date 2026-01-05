from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.urls import reverse

# Create your models here.

""" 
class Shoe(models.Model):
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('U', 'Unisex'),
        ('K', 'Kids'),
    ]
    
    CATEGORY_CHOICES = [
        ('running', 'Running'),
        ('sports', 'Sports'),
        ('casual', 'Casual'),
        ('sneakers', 'Sneakers'),
        ('athletic', 'Athletic'),
        ('formal', 'Formal'),
        ('loafers', 'Loafers'),
        ('crocs','Crocs'),
        ('heels','Heels'),
        ('dress pumps','Dress pumps'),
        ('boots', 'Boots'),
        ('sandals', 'Sandals'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    shoe_id = models.AutoField(primary_key=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='shoes')

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:shoe_details', args=[self.shoe_id])
    

class ShoeImage(models.Model):
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='shoe_images/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'Image for {self.shoe.name}'

class ShoeVariant(models.Model):
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='variants')
    color = models.CharField(max_length=50)
    size = models.IntegerField(validators=[MinValueValidator(35), MaxValueValidator(49)])
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    sku = models.CharField(max_length=100, unique=True, blank=True)
    variant_id = models.AutoField(primary_key=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f'{self.shoe.shoe_id}-{self.color[:3].upper()}-{self.size}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.shoe.name} - {self.color} - {self.size}'
    
class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    website = models.URLField()
    brand_id = models.AutoField(primary_key=True)
    
    def __str__(self):
        return self.name

class Customer (models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    wishlist = models.ManyToManyField(Shoe, through='WishlistItem', related_name='wishlisted_by_customers')
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    date_ordered = models.DateTimeField(auto_now_add=True)
    date_delivered = models.DateTimeField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    shoe_variants = models.ManyToManyField('ShoeVariant', through='OrderItem', related_name='orders')

    def total_amount(self):
        return self.sub_total + self.shipping_cost - self.discount_amount
    
    def __str__(self):
        return f'Order {self.order_id} - {self.status}'
    
class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_items')
    variant = models.ForeignKey('ShoeVariant', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'variant')

    def __str__(self):
        return f'OrderItem - {self.variant} x {self.quantity}'
    
    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.variant.shoe.price * self.quantity
        super().save(*args, **kwargs)
        self.order.sub_total = sum(item.price for item in self.order.order_items.all()) + self.price
        self.order.save()

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    comment = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    order_item = models.OneToOneField('OrderItem', on_delete=models.CASCADE, related_name='review')
    
    def __str__(self):
        return self.title

class WishlistItem(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='wishlist_items')
    shoe = models.ForeignKey('Shoe', on_delete=models.CASCADE, related_name='wishlisted_by')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'shoe')

    def __str__(self):
        return f'WishlistItem {self.shoe} for {self.customer}'
 """