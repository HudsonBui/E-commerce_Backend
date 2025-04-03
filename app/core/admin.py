"""Django admin customizations."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core import models


class UserAdmin(BaseUserAdmin):
    """Define admin pages for users."""
    ordering = ['id']
    list_display = [
        'email',
        'name',
        'phone_number',
        'address',
        'is_first_time_user',
        'is_active',
    ]


admin.site.register(models.User, UserAdmin)
