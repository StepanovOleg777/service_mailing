"""
Представления для работы с пользователями.
"""

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm, UserProfileForm
from .models import User


class UserLoginView(LoginView):
    """Представление для входа пользователя."""

    template_name = "users/login.html"
    redirect_authenticated_user = True


def user_logout(request):
    """Представление для выхода пользователя."""
    logout(request)
    request.session.flush()
    return redirect("index")


class UserRegisterView(CreateView):
    """Представление для регистрации пользователя."""

    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


class UserProfileView(LoginRequiredMixin, UpdateView):
    """Представление для просмотра и редактирования профиля."""

    model = User
    form_class = UserProfileForm
    template_name = "users/profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy("users:profile")
