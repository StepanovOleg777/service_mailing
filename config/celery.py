"""
Настройки Celery для асинхронной отправки рассылок.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Использование настроек Django для Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач
app.autodiscover_tasks(['apps.mailings'])

# Периодические задачи
app.conf.beat_schedule = {
    'send-scheduled-mailings-every-5-minutes': {
        'task': 'apps.mailings.tasks.send_scheduled_mailings',
        'schedule': 300.0,  # 5 минут
    },
}