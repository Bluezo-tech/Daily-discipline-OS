from django.urls import path
from . import admin_views

urlpatterns = [
    path("admin-panel/", admin_views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/users/<int:user_id>/", admin_views.admin_user_detail, name="admin_user_detail"),
    path("admin-panel/users/<int:user_id>/tasks/", admin_views.admin_user_tasks, name="admin_user_tasks"),
    path("admin-panel/users/<int:user_id>/habits/", admin_views.admin_user_habits, name="admin_user_habits"),
]