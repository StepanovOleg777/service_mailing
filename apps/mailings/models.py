"""
Модели для приложения рассылок.
"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from apps.users.models import User


class Client(models.Model):
    """Модель получателя рассылки (клиента)."""
    email = models.EmailField(
        _('email'),
        unique=True,
        help_text=_('Email address of the client.')
    )
    full_name = models.CharField(
        _('full name'),
        max_length=255,
        help_text=_('Full name of the client.')
    )
    comment = models.TextField(
        _('comment'),
        blank=True,
        help_text=_('Additional information about the client.')
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('owner'),
        related_name='clients',
        help_text=_('User who created this client.')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('Date and time when the client was created.')
    )

    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')
        permissions = [
            ('can_view_all_clients', 'Can view all clients'),
        ]

    def __str__(self):
        return f'{self.full_name} ({self.email})'


class Message(models.Model):
    """Модель сообщения для рассылки."""
    subject = models.CharField(
        _('subject'),
        max_length=255,
        help_text=_('Email subject line.')
    )
    body = models.TextField(
        _('body'),
        help_text=_('Email body content.')
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('owner'),
        related_name='messages',
        help_text=_('User who created this message.')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('Date and time when the message was created.')
    )

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        permissions = [
            ('can_view_all_messages', 'Can view all messages'),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """Модель рассылки."""

    class Status(models.TextChoices):
        CREATED = 'created', _('Создана')
        STARTED = 'started', _('Запущена')
        COMPLETED = 'completed', _('Завершена')

    start_time = models.DateTimeField(
        _('start time'),
        help_text=_('Date and time when mailing can start.')
    )
    end_time = models.DateTimeField(
        _('end time'),
        help_text=_('Date and time when mailing must end.')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
        help_text=_('Current status of the mailing.')
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name=_('message'),
        related_name='mailings',
        help_text=_('Message to send in this mailing.')
    )
    clients = models.ManyToManyField(
        Client,
        verbose_name=_('clients'),
        related_name='mailings',
        help_text=_('Clients who will receive this mailing.')
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('owner'),
        related_name='mailings',
        help_text=_('User who created this mailing.')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('Date and time when the mailing was created.')
    )

    class Meta:
        verbose_name = _('mailing')
        verbose_name_plural = _('mailings')
        ordering = ['-created_at']
        permissions = [
            ('can_view_all_mailings', 'Can view all mailings'),
            ('can_disable_mailing', 'Can disable mailing'),
        ]

    def __str__(self):
        return f'Рассылка #{self.id} ({self.get_status_display()})'

    def update_status(self):
        """Обновляет статус рассылки на основе текущего времени."""
        now = timezone.now()

        if now < self.start_time:
            new_status = self.Status.CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.Status.STARTED
        else:
            new_status = self.Status.COMPLETED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def clean(self):
        """Валидация дат рассылки."""
        now = timezone.now()

        if self.start_time < now:
            raise ValidationError({
                'start_time': _('Start time cannot be in the past.')
            })

        if self.start_time >= self.end_time:
            raise ValidationError({
                'end_time': _('End time must be after start time.')
            })

    def can_send(self):
        """Проверяет, можно ли отправлять рассылку."""
        now = timezone.now()
        return self.start_time <= now <= self.end_time


class MailingAttempt(models.Model):
    """Модель попытки отправки рассылки."""

    class Status(models.TextChoices):
        SUCCESS = 'success', _('Успешно')
        FAILURE = 'failure', _('Не успешно')

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        verbose_name=_('mailing'),
        related_name='attempts',
        help_text=_('Mailing associated with this attempt.')
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name=_('client'),
        related_name='attempts',
        help_text=_('Client who received the email.')
    )
    attempt_time = models.DateTimeField(
        _('attempt time'),
        auto_now_add=True,
        help_text=_('Date and time of the sending attempt.')
    )
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        help_text=_('Status of the sending attempt.')
    )
    server_response = models.TextField(
        _('server response'),
        blank=True,
        help_text=_('Response from the mail server.')
    )

    class Meta:
        verbose_name = _('mailing attempt')
        verbose_name_plural = _('mailing attempts')
        ordering = ['-attempt_time']

    def __str__(self):
        return f'Попытка #{self.id} - {self.get_status_display()}'