from django.urls import path
from . import admin_views

app_name = 'admin_panel'

urlpatterns = [
    path('', admin_views.admin_dashboard, name='dashboard'),
    path('users/', admin_views.admin_users, name='users'),
    path('users/<int:user_id>/', admin_views.admin_user_detail, name='user_detail'),
    path('users/<int:user_id>/tasks/', admin_views.admin_user_tasks, name='user_tasks'),
    path('users/<int:user_id>/habits/', admin_views.admin_user_habits, name='user_habits'),
    path('notifications/create/', admin_views.admin_create_notification, name='create_notification'),
]