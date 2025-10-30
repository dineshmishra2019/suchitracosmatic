from django.contrib import admin
from .models import Profile, Address

# Register your models here.

class AddressInline(admin.StackedInline):
    """Allows admin to see user addresses from within the Profile page."""
    model = Address
    extra = 1

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    inlines = [AddressInline]
