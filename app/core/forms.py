from django import forms
from core import models


class BroadcastNotificationForm(forms.Form):
    """Form for creating a notification to send to all users."""
    type = forms.ChoiceField(
        choices=models.Notification.type.field.choices,
        label="Notification Type",
        initial="system",
    )
    title = forms.CharField(
        max_length=255,
        label="Title",
        required=True,
    )
    message = forms.CharField(
        widget=forms.Textarea,
        label="Message",
        required=True,
    )
    is_read = forms.BooleanField(
        label="Mark as read",
        required=False,
        initial=False,
    )
