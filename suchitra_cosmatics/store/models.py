from django.db import models
from django.conf import settings
from django.urls import reverse

class Category(models.Model):
    """Model for product categories."""
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True, help_text="Banner image for the category page")

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])

class Product(models.Model):
    """Model for individual products."""
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.CharField(max_length=100, db_index=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, help_text="Short description shown on the product detail page.")
    ingredients = models.TextField(blank=True, help_text="Ingredient list for the accordion section.")
    how_to_use = models.TextField(blank=True, help_text="'How to Use' instructions for the accordion section.")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Display on homepage?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

class ProductImage(models.Model):
    """Handles the product image gallery."""
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d', help_text="Product image (ideally 400x500px)")
    alt_text = models.CharField(max_length=255, blank=True, help_text="Descriptive text for accessibility")
    is_main_image = models.BooleanField(default=False, help_text="Is this the main image for the product?")

    def __str__(self):
        return f"Image for {self.product.name}"

class Review(models.Model):
    """Handles product reviews and ratings."""
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'Review by {self.user} for {self.product}'

class Order(models.Model):
    """Model for customer orders."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    # Store addresses as text to decouple from user profile changes after order placement
    shipping_address = models.TextField()
    billing_address = models.TextField()
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=50, default='Pending') # e.g., Pending, Shipped, Delivered
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

class OrderItem(models.Model):
    """Represents a single item within an order."""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

class Testimonial(models.Model):
    """For the homepage testimonials section."""
    customer_name = models.CharField(max_length=100)
    quote = models.TextField()
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True, help_text="Customer headshot")
    is_featured = models.BooleanField(default=False, help_text="Display on homepage?")

    def __str__(self):
        return f"Testimonial by {self.customer_name}"