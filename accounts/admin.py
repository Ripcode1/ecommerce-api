from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'is_seller', 'is_active', 'date_joined']
    list_filter = ['is_seller', 'is_active', 'is_staff']
    search_fields = ['email', 'username']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {
            'fields': (
                'phone_number', 'address', 'city',
                'country', 'date_of_birth', 'is_seller'
            ),
        }),
    )
