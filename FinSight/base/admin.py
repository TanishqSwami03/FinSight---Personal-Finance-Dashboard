from django.contrib import admin
from .forms import *
from .models import *
# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserCreationForm  # Use the existing signup form
    list_display = ('email', 'first_name', 'last_name', 'mobile_number', 'mobile_code', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)