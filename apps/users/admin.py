"""
Административная панель для пользователей.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Кастомная админка для пользователей."""
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_blocked')
    list_filter = ('is_staff', 'is_superuser', 'is_blocked', 'country')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'avatar', 'phone', 'country')}),
        (_('Permissions'),
         {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_blocked', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )