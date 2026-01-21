"""
ASGI конфигурация для проекта service_mailing.

Этот модуль содержит ASGI приложение, которое может обслуживать Django проект.

Он предоставляет точку входа для асинхронных веб-серверов, совместимых с ASGI.
"""

import os
from django.core.asgi import get_asgi_application

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Получаем ASGI приложение Django
application = get_asgi_application()
