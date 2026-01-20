"""
Административная панель для рассылок.
"""
from django.contrib import admin
from .models import Client, Message, Mailing, MailingAttempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Админка для клиентов."""
    list_display = ('email', 'full_name', 'owner', 'created_at')
    list_filter = ('owner', 'created_at')
    search_fields = ('email', 'full_name')
    readonly_fields = ('created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Админка для сообщений."""
    list_display = ('subject', 'owner', 'created_at')
    list_filter = ('owner', 'created_at')
    search_fields = ('subject', 'body')
    readonly_fields = ('created_at',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Админка для рассылок."""
    list_display = ('id', 'status', 'start_time', 'end_time', 'owner', 'created_at')
    list_filter = ('status', 'owner', 'created_at')
    search_fields = ('message__subject',)
    filter_horizontal = ('clients',)
    readonly_fields = ('status', 'created_at')
    actions = ['force_update_status']

    def force_update_status(self, request, queryset):
        """Принудительное обновление статуса рассылок."""
        for mailing in queryset:
            mailing.update_status()
        self.message_user(request, f'Статус обновлен для {queryset.count()} рассылок')

    force_update_status.short_description = 'Обновить статус выбранных рассылок'


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """Админка для попыток рассылки."""
    list_display = ('id', 'mailing', 'client', 'status', 'attempt_time')
    list_filter = ('status', 'attempt_time')
    search_fields = ('client__email', 'server_response')
    readonly_fields = ('attempt_time',)