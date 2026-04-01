from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)

    due_date = models.DateField(default=timezone.now)
    due_time = models.TimeField(blank=True, null=True)

    reminder_enabled = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['completed', 'due_date', 'due_time', '-created_at']

    def __str__(self):
        return self.title

    def toggle_complete(self):
        """Toggle the completed status of the task."""
        self.completed = not self.completed
        self.save()
        return self.completed

    def get_due_datetime(self):
        """Return the combined due date and time."""
        if self.due_time:
            due_datetime = datetime.combine(self.due_date, self.due_time)
        else:
            due_datetime = datetime.combine(self.due_date, datetime.min.time())

        if timezone.is_naive(due_datetime):
            due_datetime = timezone.make_aware(
                due_datetime,
                timezone.get_current_timezone()
            )

        return due_datetime

    def is_overdue(self):
        """Check if the task is overdue."""
        if self.completed:
            return False

        due_datetime = self.get_due_datetime()
        return timezone.now() > due_datetime

    def should_remind_now(self):
        """Check if reminder should trigger."""
        if not self.reminder_enabled:
            return False

        if self.reminder_sent:
            return False

        if not self.due_date:
            return False

        due_datetime = self.get_due_datetime()

        return timezone.now() >= due_datetime