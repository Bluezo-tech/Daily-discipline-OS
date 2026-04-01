def notification_context(request):
    notifications = []
    unread_count = 0

    try:
        user = getattr(request, "user", None)

        if user and user.is_authenticated and hasattr(user, "notifications"):
            notifications = user.notifications.all().order_by("-created_at")[:5]
            unread_count = user.notifications.filter(is_read=False).count()
    except Exception:
        notifications = []
        unread_count = 0

    return {
        "header_notifications": notifications,
        "unread_notifications_count": unread_count,
    }