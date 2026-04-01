"""
URL configuration for daily_discipline_os project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import root_redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin-panel/", include("accounts.admin_urls")),
    path("", root_redirect, name="root"),
    path("", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("tasks/", include("tasks.urls")),
    path("habits/", include("habits.urls")),
    path("achievements/", include("achievements.urls")),
    path("notifications/", include("notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)