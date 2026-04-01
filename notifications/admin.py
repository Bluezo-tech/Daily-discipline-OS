import uuid

from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Notification

User = get_user_model()


class NotificationAdminForm(forms.ModelForm):
    send_to_all = forms.BooleanField(
        required=False,
        label="Send to all users"
    )

    class Meta:
        model = Notification
        fields = [
            "user",
            "title",
            "message",
            "notification_type",
            "action_url",
            "action_text",
            "is_read",
            "is_admin_notification",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].required = False

        if self.instance and self.instance.pk and self.instance.broadcast_id:
            self.fields["send_to_all"].initial = True

    def clean(self):
        cleaned_data = super().clean()
        send_to_all = cleaned_data.get("send_to_all")
        user = cleaned_data.get("user")

        if not send_to_all and not user:
            raise forms.ValidationError("Select one user or tick 'Send to all users'.")

        return cleaned_data


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm

    list_display = (
        "title",
        "user",
        "notification_type",
        "is_read",
        "is_admin_notification",
        "has_action_link",
        "broadcast_status",
        "created_at",
    )
    list_filter = (
        "notification_type",
        "is_read",
        "is_admin_notification",
        "created_at",
    )
    search_fields = (
        "title",
        "message",
        "user__email",
        "action_url",
        "action_text",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Notification Details", {
            "fields": (
                ("user", "send_to_all"),
                "title",
                "message",
                "notification_type",
            )
        }),
        ("Link Action", {
            "fields": (
                "action_url",
                "action_text",
            ),
            "description": "Optional clickable link for this notification.",
        }),
        ("Status", {
            "fields": (
                "is_read",
                "is_admin_notification",
                "created_at",
            )
        }),
    )

    def has_action_link(self, obj):
        return bool(obj.action_url)
    has_action_link.boolean = True
    has_action_link.short_description = "Has Link"

    def broadcast_status(self, obj):
        return bool(obj.broadcast_id)
    broadcast_status.boolean = True
    broadcast_status.short_description = "Broadcast"

    def save_model(self, request, obj, form, change):
        send_to_all = form.cleaned_data.get("send_to_all")

        # create notification for all users
        if send_to_all and not change:
            broadcast_id = str(uuid.uuid4())
            notifications = []

            for user in User.objects.filter(is_active=True):
                notifications.append(
                    Notification(
                        user=user,
                        title=form.cleaned_data["title"],
                        message=form.cleaned_data["message"],
                        notification_type=form.cleaned_data["notification_type"],
                        action_url=form.cleaned_data.get("action_url"),
                        action_text=form.cleaned_data.get("action_text"),
                        broadcast_id=broadcast_id,
                        is_read=form.cleaned_data.get("is_read", False),
                        is_admin_notification=form.cleaned_data.get("is_admin_notification", False),
                    )
                )

            Notification.objects.bulk_create(notifications)
            obj._send_to_all_done = True
            return

        # edit all copies of a broadcast notification
        if change and obj.broadcast_id:
            Notification.objects.filter(broadcast_id=obj.broadcast_id).update(
                title=form.cleaned_data["title"],
                message=form.cleaned_data["message"],
                notification_type=form.cleaned_data["notification_type"],
                action_url=form.cleaned_data.get("action_url"),
                action_text=form.cleaned_data.get("action_text"),
                is_admin_notification=form.cleaned_data.get("is_admin_notification", False),
            )
            obj._broadcast_updated = True
            return

        # normal single-user notification
        super().save_model(request, obj, form, change)

    def log_addition(self, request, obj, message):
        if getattr(obj, "_send_to_all_done", False):
            return
        super().log_addition(request, obj, message)

    def log_change(self, request, obj, message):
        if getattr(obj, "_broadcast_updated", False):
            return
        super().log_change(request, obj, message)

    def response_add(self, request, obj, post_url_continue=None):
        if getattr(obj, "_send_to_all_done", False):
            self.message_user(
                request,
                "Notification sent to all active users successfully.",
                level=messages.SUCCESS,
            )
            return HttpResponseRedirect(
                reverse("admin:notifications_notification_changelist")
            )
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if getattr(obj, "_broadcast_updated", False):
            self.message_user(
                request,
                "Broadcast notification updated for all users successfully.",
                level=messages.SUCCESS,
            )
            return HttpResponseRedirect(
                reverse("admin:notifications_notification_changelist")
            )
        return super().response_change(request, obj)