from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'due_date', 'due_time', 'priority', 'completed', 'reminder_enabled', 'created_at')
    list_filter = ('completed', 'priority', 'reminder_enabled', 'due_date', 'created_at')
    search_fields = ('title', 'notes', 'user__email')
    date_hierarchy = 'due_date'
    ordering = ('-due_date', '-created_at')