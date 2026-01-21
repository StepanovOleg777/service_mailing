"""
WSGI конфигурация для проекта service_mailing.

Этот модуль содержит WSGI приложение, которое может обслуживать Django проект.

Он предоставляет точку входа для веб-серверов, совместимых с WSGI.
"""

import os
from django.core.wsgi import get_wsgi_application

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Получаем WSGI приложение Django
application = get_wsgi_application()
