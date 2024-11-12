from django.contrib import admin
from .forms import *
from .models import *
# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserCreationForm  # Use the existing signup form
    list_display = ('email', 'first_name', 'last_name', 'mobile_number', 'mobile_code', 'is_staff', 'is_active', 'wallet_balance')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    # Add wallet_balance to the user detail view in the admin panel
    fieldsets = (
        (None, {
            'fields': ('email', 'password', 'wallet_balance')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'mobile_code', 'mobile_number')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)