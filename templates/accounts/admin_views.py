from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render

from tasks.models import Task
from habits.models import Habit

User = get_user_model()


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = User.objects.count()
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(completed=True).count()
    total_habits = Habit.objects.count()

    recent_users = list(User.objects.order_by("-date_joined")[:8])

    for u in recent_users:
        u.task_count = Task.objects.filter(user=u).count()
        u.habit_count = Habit.objects.filter(user=u).count()

    context = {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "total_habits": total_habits,
        "recent_users": recent_users,
    }
    return render(request, "admin/dashboard.html", context)


@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    user_tasks = Task.objects.filter(user=user_obj)
    user_habits = Habit.objects.filter(user=user_obj)

    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(completed=True).count()
    total_habits = user_habits.count()

    current_streak = 0
    longest_streak = 0

    for habit in user_habits:
        current_streak += getattr(habit, "current_streak", 0) or 0
        longest_streak = max(longest_streak, getattr(habit, "longest_streak", 0) or 0)

    context = {
        "user_obj": user_obj,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "total_habits": total_habits,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
    }
    return render(request, "admin/user_detail.html", context)


@login_required
@user_passes_test(is_admin)
def admin_user_tasks(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    tasks = Task.objects.filter(user=user_obj).order_by("-due_date", "-due_time", "-id")

    context = {
        "user_obj": user_obj,
        "tasks": tasks,
    }
    return render(request, "admin/user_tasks.html", context)


@login_required
@user_passes_test(is_admin)
def admin_user_habits(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    habits = Habit.objects.filter(user=user_obj).order_by("-id")

    context = {
        "user_obj": user_obj,
        "habits": habits,
    }
    return render(request, "admin/user_habits.html", context)