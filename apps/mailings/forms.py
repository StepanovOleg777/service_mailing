"""
Формы для работы с рассылками.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Client, Message, Mailing


class ClientForm(forms.ModelForm):
    """Форма для создания и редактирования клиента."""

    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MessageForm(forms.ModelForm):
    """Форма для создания и редактирования сообщения."""

    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class MailingForm(forms.ModelForm):
    """Форма для создания и редактирования рассылки."""

    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'clients']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'end_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'clients': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Фильтруем сообщения и клиентов по владельцу
        if user:
            if not user.is_superuser:
                self.fields['message'].queryset = Message.objects.filter(owner=user)
                self.fields['clients'].queryset = Client.objects.filter(owner=user)