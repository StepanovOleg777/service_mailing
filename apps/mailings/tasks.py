"""
Задачи Celery для рассылок.
"""

from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_scheduled_mailings():
    """Задача для отправки запланированных рассылок."""
    logger.info(f"Запуск автоматической отправки рассылок: {timezone.now()}")

    try:
        call_command("send_mailings")
        return "Рассылки успешно отправлены"
    except Exception as e:
        logger.error(f"Ошибка при отправке рассылок: {e}")
        return f"Ошибка: {e}"
