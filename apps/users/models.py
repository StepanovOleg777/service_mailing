"""
Модель пользователя для сервиса рассылок.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Кастомная модель пользователя."""
    username = None
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. A valid email address.')
    )
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text=_('User profile picture.')
    )
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        help_text=_('User phone number.')
    )
    country = models.CharField(
        _('country'),
        max_length=100,
        blank=True,
        help_text=_('User country.')
    )
    is_blocked = models.BooleanField(
        _('blocked'),
        default=False,
        help_text=_('Designates whether the user is blocked.')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        permissions = [
            ('can_block_user', 'Can block users'),
            ('can_view_all_mailings', 'Can view all mailings'),
        ]

    def __str__(self):
        return f'{self.email} ({self.get_full_name()})'