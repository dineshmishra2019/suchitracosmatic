from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductImage,
    Review,
    Order,
    OrderItem,
    Testimonial,
)

# Register your models here.

class ProductImageInline(admin.TabularInline):
    """Allows admin to add product images from within the Product page."""
    model = ProductImage
    extra = 1

class OrderItemInline(admin.TabularInline):
    """Allows admin to see order items from within the Order page."""
    model = OrderItem
    readonly_fields = ('product', 'price', 'quantity', 'get_cost')
    extra = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_featured', 'created_at')
    list_filter = ('is_available', 'is_featured', 'category', 'created_at')
    list_editable = ('price', 'is_available', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_paid', 'order_status', 'created_at')
    list_filter = ('order_status', 'created_at')
    inlines = [OrderItemInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'rating', 'is_featured')
    list_filter = ('is_featured',)
    list_editable = ('is_featured',)
