from django import forms
from .models import Notification


class AdminNotificationForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Notification title'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 4,
            'placeholder': 'Notification message'
        })
    )
    notification_type = forms.ChoiceField(
        choices=[
            ('admin', 'Admin Announcement'),
            ('update', 'App Update'),
            ('maintenance', 'Maintenance'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )