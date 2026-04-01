from django.conf import settings
from django.db import models


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("admin", "Admin Notification"),
        ("task", "Task"),
        ("habit", "Habit"),
        ("achievement", "Achievement"),
        ("reminder", "Reminder"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default="task",
    )
    action_url = models.URLField(blank=True, null=True)
    action_text = models.CharField(max_length=100, blank=True, null=True)
    broadcast_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    is_read = models.BooleanField(default=False)
    is_admin_notification = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.user_id and hasattr(self.user, "email"):
            return f"{self.user.email} - {self.title}"
        return self.title

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=["is_read"])

    @property
    def has_action(self):
        return bool(self.action_url)

    @property
    def is_broadcast(self):
        return bool(self.broadcast_id)