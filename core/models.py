from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime  # ADD THIS IMPORT

class Profile(models.Model):
    USER_TYPES = (
        ('farmer', 'Farmer'),
        ('dealer', 'Fertilizer Dealer'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=100, default='')
    pincode = models.CharField(max_length=10, default='')
    
    # Farmer specific fields
    farm_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    farm_location = models.CharField(max_length=200, blank=True, null=True)
    
    # Dealer specific fields
    company_name = models.CharField(max_length=200, blank=True, null=True)
    business_address = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
    
    def is_farmer(self):
        return self.user_type == 'farmer'
    
    def is_dealer(self):
        return self.user_type == 'dealer'

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    dealer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    
    # IMAGE FIELD ADDED HERE
    image = models.ImageField(upload_to='products/', blank=True, null=True, default='products/default.jpg')    
    # Fertilizer specific fields
    nitrogen_content = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    phosphorus_content = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    potassium_content = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    suitable_crops = models.TextField(blank=True)
    usage_instructions = models.TextField(blank=True)
    
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def in_stock(self):
        return self.stock_quantity > 0
    
    def npk_ratio(self):
        return f"N:{self.nitrogen_content}% P:{self.phosphorus_content}% K:{self.potassium_content}%"
    
    # Helper method to get image URL
    def get_image_url(self):
        if self.image:
            return self.image.url
        return '/media/products/default.jpg'

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart - {self.user.username}"
    
    def total_items(self):
        try:
            return sum(item.quantity for item in self.cartitem_set.all())
        except:
            return 0
    
    def total_price(self):
        try:
            return sum(item.total_price() for item in self.cartitem_set.all())
        except:
            return 0
    
    class Meta:
        pass

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def total_price(self):
        return self.product.price * self.quantity
    
    class Meta:
        unique_together = ['cart', 'product']

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Shipping address
    shipping_full_name = models.CharField(max_length=255)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_pincode = models.CharField(max_length=10)
    shipping_phone = models.CharField(max_length=15)
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Tracking information - FIXED: Use models.DateTimeField instead of datetime.datetime
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)  # FIXED THIS LINE
    delivered_at = models.DateTimeField(blank=True, null=True)  # FIXED THIS LINE
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number when first saving
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.order_number = f"ORD{timestamp}"
        super().save(*args, **kwargs)
    
    def get_status_badge(self):
        status_colors = {
            'pending': 'secondary',
            'confirmed': 'info',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_payment_badge(self):
        payment_colors = {
            'pending': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'refunded': 'info'
        }
        return payment_colors.get(self.payment_status, 'secondary')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    dealer = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    item_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def save(self, *args, **kwargs):
        self.item_total = self.price * self.quantity
        super().save(*args, **kwargs)

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating} Stars"
    
    class Meta:
        unique_together = ['user', 'product']