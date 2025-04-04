"""Django admin customizations."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

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
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Personal Info'), {'fields': ('name', 'phone_number', 'address')}),
        (_('Important Dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ('last_login',)
    add_fieldsets = (
        (None, {
            'classes': ('wide', 'extrapretty'),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'phone_number',
                'address',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )


admin.site.register(models.User, UserAdmin)
