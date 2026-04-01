from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from notifications.models import Notification
from .models import Task


def _parse_due_date(date_str):
    if not date_str:
        return timezone.now().date()
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return timezone.now().date()


def _parse_due_time(time_str):
    if not time_str:
        return None
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return None


def _safe_next_url(request, default_name="tasks:today_tasks"):
    return request.POST.get("next") or request.META.get("HTTP_REFERER") or default_name


def _build_google_calendar_url(task):
    if not task.due_date:
        return ""

    title = task.title or "Task Reminder"
    notes = task.notes or ""

    if task.due_time:
        start_dt = datetime.combine(task.due_date, task.due_time)
        end_dt = start_dt + timedelta(minutes=30)
        dates = f"{start_dt.strftime('%Y%m%dT%H%M%S')}/{end_dt.strftime('%Y%m%dT%H%M%S')}"
    else:
        start_date = task.due_date.strftime("%Y%m%d")
        end_date = (task.due_date + timedelta(days=1)).strftime("%Y%m%d")
        dates = f"{start_date}/{end_date}"

    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": dates,
        "details": notes,
    }
    return "https://calendar.google.com/calendar/render?" + urlencode(params)


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by(
        "completed", "due_date", "due_time", "-created_at"
    )
    context = {
        "tasks": tasks,
        "title": "All Tasks",
        "view_type": "all",
    }
    return render(request, "tasks/task_list.html", context)


@login_required
def today_tasks(request):
    today = timezone.now().date()
    tasks = Task.objects.filter(user=request.user, due_date=today).order_by(
        "completed", "due_time", "-created_at"
    )
    incomplete_tasks = tasks.filter(completed=False)
    completed_tasks = tasks.filter(completed=True)

    context = {
        "incomplete_tasks": incomplete_tasks,
        "completed_tasks": completed_tasks,
        "title": "Today's Tasks",
        "view_type": "today",
        "today": today,
    }
    return render(request, "tasks/today_tasks.html", context)


@login_required
def upcoming_tasks(request):
    today = timezone.now().date()
    next_week = today + timedelta(days=7)

    tasks = list(
        Task.objects.filter(
            user=request.user,
            due_date__gte=today,
            due_date__lte=next_week
        ).order_by("due_date", "due_time", "completed", "-created_at")
    )

    for task in tasks:
        task.google_calendar_url = _build_google_calendar_url(task)

    context = {
        "tasks": tasks,
        "title": "Upcoming Tasks (Next 7 Days)",
        "view_type": "upcoming",
        "today": today,
    }
    return render(request, "tasks/upcoming_tasks.html", context)


@login_required
def task_create(request):
    if request.method != "POST":
        return redirect("tasks:today_tasks")

    title = request.POST.get("title", "").strip()
    notes = request.POST.get("notes", "").strip()
    due_date_str = request.POST.get("due_date", "")
    due_time_str = request.POST.get("due_time", "")
    priority = request.POST.get("priority", "medium")
    reminder_enabled = request.POST.get("reminder_enabled") == "on"

    if not title:
        messages.error(request, "Task title is required.")
        return redirect(_safe_next_url(request))

    due_date = _parse_due_date(due_date_str)
    due_time = _parse_due_time(due_time_str)

    Task.objects.create(
        user=request.user,
        title=title,
        notes=notes or None,
        due_date=due_date,
        due_time=due_time,
        priority=priority,
        reminder_enabled=reminder_enabled,
        reminder_sent=False,
    )

    messages.success(request, f'Task "{title}" created successfully.')
    return redirect(_safe_next_url(request))


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method != "POST":
        return redirect("tasks:today_tasks")

    title = request.POST.get("title", "").strip()
    notes = request.POST.get("notes", "").strip()
    due_date_str = request.POST.get("due_date", "")
    due_time_str = request.POST.get("due_time", "")
    priority = request.POST.get("priority", "medium")
    reminder_enabled = request.POST.get("reminder_enabled") == "on"

    if not title:
        messages.error(request, "Task title is required.")
        return redirect(_safe_next_url(request))

    task.title = title
    task.notes = notes or None
    task.priority = priority
    task.reminder_enabled = reminder_enabled
    task.reminder_sent = False
    task.due_date = _parse_due_date(due_date_str)
    task.due_time = _parse_due_time(due_time_str)
    task.save()

    messages.success(request, f'Task "{title}" updated successfully.')
    return redirect(_safe_next_url(request))


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == "POST":
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully.')

    return redirect(_safe_next_url(request))


@login_required
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == "POST":
        was_completed = task.completed
        is_completed = task.toggle_complete()

        if is_completed:
            Notification.objects.create(
                user=request.user,
                title="Task Completed",
                message=f'You completed the task: "{task.title}"',
                notification_type="task",
            )
        elif was_completed and not is_completed:
            Notification.objects.create(
                user=request.user,
                title="Task Marked Incomplete",
                message=f'You marked the task as incomplete again: "{task.title}"',
                notification_type="task",
            )

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "completed": is_completed,
                "task_id": task.id,
            })

        status = "completed" if is_completed else "marked as incomplete"
        messages.success(request, f'Task "{task.title}" {status}.')

    return redirect(_safe_next_url(request))


@login_required
def check_reminders(request):
    today = timezone.localdate()

    tasks = Task.objects.filter(
        user=request.user,
        reminder_enabled=True,
        completed=False,
        reminder_sent=False,
        due_date=today,
    ).order_by("due_date", "due_time")

    reminders = []

    for task in tasks:
        if not task.due_time:
            continue

        if task.should_remind_now():
            reminders.append({
                "id": task.id,
                "title": task.title,
                "notes": task.notes or "",
                "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else None,
                "due_time": task.due_time.strftime("%H:%M") if task.due_time else None,
            })

            task.reminder_sent = True
            task.save(update_fields=["reminder_sent"])

            if not Notification.objects.filter(
                user=request.user,
                title="Task Reminder",
                message__contains=task.title,
                created_at__date=today,
            ).exists():
                Notification.objects.create(
                    user=request.user,
                    title="Task Reminder",
                    message=f'Reminder for task: "{task.title}"',
                    notification_type="task",
                )

    return JsonResponse({"reminders": reminders})


def check_missed_tasks(user):
    return