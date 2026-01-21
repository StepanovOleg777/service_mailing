"""
Модель пользователя для сервиса рассылок.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Кастомная модель пользователя."""

    avatar = models.ImageField(
        _("аватар"),
        upload_to="avatars/",
        null=True,
        blank=True,
        help_text=_("Изображение профиля пользователя."),
    )
    phone = models.CharField(
        _("номер телефона"),
        max_length=20,
        blank=True,
        help_text=_("Номер телефона пользователя."),
    )
    country = models.CharField(
        _("страна"), max_length=100, blank=True, help_text=_("Страна пользователя.")
    )
    is_blocked = models.BooleanField(
        _("заблокирован"),
        default=False,
        help_text=_("Указывает, заблокирован ли пользователь."),
    )

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
        permissions = [
            ("can_block_user", "Может блокировать пользователей"),
            ("can_view_all_mailings", "Может просматривать все рассылки"),
        ]

    def __str__(self):
        """Строковое представление пользователя."""
        full_name = self.get_full_name()
        if full_name:
            return f"{self.username} ({full_name})"
        return self.username

    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else None

    def get_short_name(self):
        """Возвращает короткое имя пользователя."""
        return self.first_name
