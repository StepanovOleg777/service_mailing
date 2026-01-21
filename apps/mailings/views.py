"""
Представления для работы с рассылками.
"""

from django.contrib import messages as django_messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)

from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm


def index(request):
    """
    Главная страница с общей статистикой.
    """
    context = {
        "total_mailings": Mailing.objects.count(),
        "active_mailings": Mailing.objects.filter(status="started").count(),
        "unique_clients": Client.objects.values("email").distinct().count(),
    }
    return render(request, "index.html", context)


# Client Views
class ClientListView(LoginRequiredMixin, ListView):
    """
    Список клиентов.
    """

    model = Client
    template_name = "mailings/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        return Client.objects.all().order_by("-created_at")


class ClientCreateView(LoginRequiredMixin, CreateView):
    """
    Создание нового клиента.
    """

    model = Client
    form_class = ClientForm
    template_name = "mailings/client_form.html"
    success_url = reverse_lazy("mailings:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        django_messages.success(self.request, "Клиент успешно создан")
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование клиента.
    """

    model = Client
    form_class = ClientForm
    template_name = "mailings/client_form.html"
    success_url = reverse_lazy("mailings:client_list")

    def form_valid(self, form):
        django_messages.success(self.request, "Клиент успешно обновлен")
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """
    Удаление клиента.
    """

    model = Client
    template_name = "mailings/client_confirm_delete.html"
    success_url = reverse_lazy("mailings:client_list")

    def delete(self, request, *args, **kwargs):
        django_messages.success(request, "Клиент успешно удален")
        return super().delete(request, *args, **kwargs)


# Message Views
class MessageListView(LoginRequiredMixin, ListView):
    """
    Список сообщений.
    """

    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.all().order_by("-created_at")


class MessageCreateView(LoginRequiredMixin, CreateView):
    """
    Создание нового сообщения.
    """

    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        django_messages.success(self.request, "Сообщение успешно создано")
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование сообщения.
    """

    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form):
        django_messages.success(self.request, "Сообщение успешно обновлено")
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """
    Удаление сообщения.
    """

    model = Message
    template_name = "mailings/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")

    def delete(self, request, *args, **kwargs):
        django_messages.success(request, "Сообщение успешно удалено")
        return super().delete(request, *args, **kwargs)


# Mailing Views
class MailingListView(LoginRequiredMixin, ListView):
    """
    Список рассылок.
    """

    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        return (
            Mailing.objects.all().select_related("message").prefetch_related("clients")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Обновляем статусы всех рассылок
        for mailing in context["mailings"]:
            mailing.update_status()
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    """
    Создание новой рассылки.
    """

    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        self.object.update_status()
        django_messages.success(self.request, "Рассылка успешно создана")
        return response


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование рассылки.
    """

    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def form_valid(self, form):
        django_messages.success(self.request, "Рассылка успешно обновлена")
        return super().form_valid(form)


class MailingDetailView(LoginRequiredMixin, DetailView):
    """
    Просмотр деталей рассылки.
    """

    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.object

        # Получаем статистику по попыткам
        attempts = mailing.attempts.select_related("client").order_by("-attempt_time")
        context["attempts"] = attempts
        context["success_count"] = attempts.filter(status="success").count()
        context["failure_count"] = attempts.filter(status="failure").count()
        context["total_attempts"] = attempts.count()

        # Получаем клиентов рассылки
        context["mailing_clients"] = mailing.clients.all()

        return context


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """
    Удаление рассылки.
    """

    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def delete(self, request, *args, **kwargs):
        django_messages.success(request, "Рассылка успешно удалена")
        return super().delete(request, *args, **kwargs)


class MailingAttemptListView(LoginRequiredMixin, ListView):
    """
    Список попыток рассылки.
    """

    model = MailingAttempt
    template_name = "mailings/attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        return (
            MailingAttempt.objects.all()
            .select_related("mailing", "client")
            .order_by("-attempt_time")
        )


def send_mailing_now(request, pk):
    """
    Ручная отправка рассылки через интерфейс.
    """
    if not request.user.is_authenticated:
        return redirect("users:login")

    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверка возможности отправки
    if not mailing.can_send():
        django_messages.error(
            request,
            f"Рассылка не может быть отправлена. "
            f"Текущее время должно быть между {mailing.start_time} и {mailing.end_time}",
        )
        return redirect("mailings:mailing_list")

    # Отправка писем
    success_count = 0
    failure_count = 0

    for client in mailing.clients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=None,
                recipient_list=[client.email],
                fail_silently=False,
            )

            # Создание записи об успешной попытке
            MailingAttempt.objects.create(
                mailing=mailing,
                client=client,
                status="success",
                server_response="Email sent successfully via web interface",
            )
            success_count += 1

        except Exception as e:
            # Создание записи о неудачной попытке
            MailingAttempt.objects.create(
                mailing=mailing, client=client, status="failure", server_response=str(e)
            )
            failure_count += 1

    # Обновляем статус рассылки
    mailing.update_status()

    django_messages.success(
        request,
        f"Рассылка #{mailing.id} отправлена. "
        f"Успешно: {success_count}, Неудачно: {failure_count}",
    )

    return redirect("mailings:mailing_detail", pk=mailing.pk)
