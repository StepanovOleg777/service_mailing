"""Утилита командной строки Django для административных задач."""

import os
import sys


def main():
    """Запуск административных задач."""
    # Устанавливаем переменную окружения для настроек Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    try:
        # Пытаемся импортировать execute_from_command_line из Django
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Если Django не установлен, выбрасываем понятную ошибку
        raise ImportError(
            "Не удалось импортировать Django. Вы уверены, что он установлен и "
            "доступен в переменной окружения PYTHONPATH? Возможно, вы забыли "
            "активировать виртуальное окружение?"
        ) from exc

    # Выполняем команду, переданную через командную строку
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
