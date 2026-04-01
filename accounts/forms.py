from django import forms
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
from .models import User


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'avatar': forms.FileInput(attrs={'class': 'form-file'}),
        }


class PasswordChangeForm(BasePasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-input'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-input'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-input'})