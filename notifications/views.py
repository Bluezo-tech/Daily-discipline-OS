from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)

    filter_type = request.GET.get("filter", "all")
    if filter_type == "unread":
        notifications = notifications.filter(is_read=False)
    elif filter_type == "read":
        notifications = notifications.filter(is_read=True)

    context = {
        "notifications": notifications,
        "unread_count": Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count(),
        "filter_type": filter_type,
    }
    return render(request, "notifications/notification_list.html", context)


@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)

    if request.method == "POST":
        notification.mark_as_read()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "unread_count": Notification.objects.filter(
                    user=request.user,
                    is_read=False
                ).count()
            })

    return redirect("notifications:notification_list")


@login_required
def mark_all_as_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True})

    return redirect("notifications:notification_list")


@login_required
def notification_dropdown(request):
    notifications = Notification.objects.filter(user=request.user)[:10]

    notifications_data = []
    for n in notifications:
        notifications_data.append({
            "id": n.id,
            "title": n.title,
            "message": n.message[:100] + "..." if len(n.message) > 100 else n.message,
            "type": n.notification_type,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%b %d, %Y %H:%M"),
            "action_url": n.action_url or "",
            "action_text": n.action_text or "",
            "has_action": bool(n.action_url),
        })

    return JsonResponse({
        "notifications": notifications_data,
        "unread_count": Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
    })