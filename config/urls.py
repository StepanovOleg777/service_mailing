"""
Основные URL-маршруты проекта.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.mailings.views import index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("users/", include("apps.users.urls")),
    path("mailings/", include("apps.mailings.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
