"""
Кастомная команда для отправки рассылок.
"""

import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from apps.mailings.models import Mailing, MailingAttempt

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Команда для отправки запланированных рассылок."""

    help = "Send scheduled mailings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--mailing-id",
            type=int,
            help="ID конкретной рассылки для отправки",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Принудительная отправка вне временного интервала",
        )

    def handle(self, *args, **options):
        mailing_id = options.get("mailing_id")
        force = options.get("force")

        if mailing_id:
            mailings = Mailing.objects.filter(id=mailing_id)
        else:
            # Получаем все активные рассылки
            mailings = Mailing.objects.filter(status="started")

        total_sent = 0
        total_failed = 0

        for mailing in mailings:
            self.stdout.write(f"Обработка рассылки #{mailing.id}")

            # Обновляем статус
            mailing.update_status()

            # Проверяем возможность отправки
            if not mailing.can_send() and not force:
                self.stdout.write(
                    f"  Пропуск: вне временного интервала "
                    f"({mailing.start_time} - {mailing.end_time})"
                )
                continue

            sent, failed = self.send_mailing(mailing)
            total_sent += sent
            total_failed += failed

        self.stdout.write(
            self.style.SUCCESS(
                f"Отправка завершена. "
                f"Успешно: {total_sent}, Неудачно: {total_failed}"
            )
        )

    def send_mailing(self, mailing):
        """Отправляет одну рассылку."""
        sent = 0
        failed = 0

        for client in mailing.clients.all():
            try:
                if mailing.attempts.filter(client=client).exists():
                    logger.info(f"  Клиенту {client.email} уже отправляли")
                    continue

                # Отправляем письмо
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=None,
                    recipient_list=[client.email],
                    fail_silently=False,
                )

                # Логируем успех
                MailingAttempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status="success",
                    server_response="Email sent successfully via command",
                )
                sent += 1
                self.stdout.write(f"  ✓ Отправлено клиенту: {client.email}")

            except Exception as e:
                # Логируем ошибку
                error_msg = str(e)
                MailingAttempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status="failure",
                    server_response=error_msg,
                )
                failed += 1
                self.stdout.write(f"  ✗ Ошибка для {client.email}: {error_msg}")
                logger.error(f"Ошибка отправки: {error_msg}")

        return sent, failed
