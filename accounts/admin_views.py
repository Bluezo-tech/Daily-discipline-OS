from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import User
from tasks.models import Task
from habits.models import Habit
from notifications.models import Notification
from notifications.forms import AdminNotificationForm


def is_admin(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard overview."""
    total_users = User.objects.filter(is_staff=False).count()
    total_tasks = Task.objects.count()
    total_habits = Habit.objects.count()
    total_notifications = Notification.objects.count()
    
    # Recent activity
    recent_users = User.objects.filter(is_staff=False).order_by('-created_at')[:5]
    recent_tasks = Task.objects.order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_tasks': total_tasks,
        'total_habits': total_habits,
        'total_notifications': total_notifications,
        'recent_users': recent_users,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'admin/dashboard.html', context)


@user_passes_test(is_admin)
def admin_users(request):
    """List all users."""
    users = User.objects.filter(is_staff=False).order_by('-created_at')
    
    # Add stats for each user
    users_with_stats = []
    for user in users:
        users_with_stats.append({
            'user': user,
            'task_count': Task.objects.filter(user=user).count(),
            'habit_count': Habit.objects.filter(user=user).count(),
            'completed_tasks': Task.objects.filter(user=user, completed=True).count(),
        })
    
    context = {
        'users': users_with_stats,
    }
    return render(request, 'admin/users.html', context)


@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """View user details."""
    user = get_object_or_404(User, id=user_id, is_staff=False)
    
    context = {
        'user_obj': user,
        'task_count': Task.objects.filter(user=user).count(),
        'habit_count': Habit.objects.filter(user=user).count(),
        'completed_tasks': Task.objects.filter(user=user, completed=True).count(),
    }
    return render(request, 'admin/user_detail.html', context)


@user_passes_test(is_admin)
def admin_user_tasks(request, user_id):
    """View user's tasks."""
    user = get_object_or_404(User, id=user_id, is_staff=False)
    tasks = Task.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user_obj': user,
        'tasks': tasks,
    }
    return render(request, 'admin/user_tasks.html', context)


@user_passes_test(is_admin)
def admin_user_habits(request, user_id):
    """View user's habits."""
    user = get_object_or_404(User, id=user_id, is_staff=False)
    habits = Habit.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user_obj': user,
        'habits': habits,
    }
    return render(request, 'admin/user_habits.html', context)


@user_passes_test(is_admin)
def admin_create_notification(request):
    """Create admin notification for all users."""
    if request.method == 'POST':
        form = AdminNotificationForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            message = form.cleaned_data['message']
            notification_type = form.cleaned_data['notification_type']
            
            # Create notification for all non-staff users
            users = User.objects.filter(is_staff=False)
            for user in users:
                Notification.objects.create(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    is_admin_notification=True
                )
            
            messages.success(request, f'Notification sent to {users.count()} users!')
            return redirect('admin_panel:dashboard')
    else:
        form = AdminNotificationForm()
    
    return render(request, 'admin/create_notification.html', {'form': form})