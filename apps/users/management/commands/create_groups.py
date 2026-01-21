"""
Команда для создания групп и прав доступа.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.mailings.models import Client, Message, Mailing
from apps.users.models import User


class Command(BaseCommand):
    """Создает группы пользователей и назначает права."""

    help = "Create user groups and assign permissions"

    def handle(self, *args, **options):
        # Создаем группу менеджеров
        managers_group, created = Group.objects.get_or_create(name="Менеджеры")

        if created:
            self.stdout.write('Группа "Менеджеры" создана')
        else:
            self.stdout.write('Группа "Менеджеры" уже существует')

        # Получаем разрешения
        content_types = {
            "client": ContentType.objects.get_for_model(Client),
            "message": ContentType.objects.get_for_model(Message),
            "mailing": ContentType.objects.get_for_model(Mailing),
            "user": ContentType.objects.get_for_model(User),
        }

        # Добавляем разрешения менеджерам
        permissions = [
            # Просмотр всех объектов
            Permission.objects.get(
                codename="can_view_all_clients", content_type=content_types["client"]
            ),
            Permission.objects.get(
                codename="can_view_all_messages", content_type=content_types["message"]
            ),
            Permission.objects.get(
                codename="can_view_all_mailings", content_type=content_types["mailing"]
            ),
            # Блокировка пользователей
            Permission.objects.get(
                codename="can_block_user", content_type=content_types["user"]
            ),
            # Отключение рассылок
            Permission.objects.get(
                codename="can_disable_mailing", content_type=content_types["mailing"]
            ),
        ]

        managers_group.permissions.set(permissions)
        managers_group.save()

        self.stdout.write(self.style.SUCCESS('Права назначены группе "Менеджеры"'))

        self.create_test_manager()

    def create_test_manager(self):
        """Создает тестового пользователя-менеджера."""
        try:
            manager, created = User.objects.get_or_create(
                email="manager@example.com",
                defaults={
                    "first_name": "Manager",
                    "last_name": "Test",
                    "is_staff": True,
                },
            )

            if created:
                manager.set_password("manager123")
                manager.save()

                # Добавляем в группу менеджеров
                managers_group = Group.objects.get(name="Менеджеры")
                manager.groups.add(managers_group)

                self.stdout.write(self.style.SUCCESS("Тестовый менеджер создан"))
                self.stdout.write("  Email: manager@example.com")
                self.stdout.write("  Password: manager123")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Ошибка создания менеджера: {e}"))
