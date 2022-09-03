from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

import qrcode
import datetime
from calendar import monthrange
import os
from pathlib import Path

from .forms import *
from .models import *


def _get_today_habits(user_id):
    """Получение привычек на день"""
    user_habits = Habits.objects.filter(user=user_id)
    print(user_habits)
    today_habits = Tracking.objects.filter(day=datetime.date.today(), habit__in=user_habits)
    if len(today_habits) == 0:
        objects_list = []
        for d in range(1, monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]+1):
            for habit in Habits.objects.filter(user=user_id):
                objects_list.append(Tracking(habit=habit,
                                             day=f'{datetime.datetime.now().year}-{datetime.datetime.now().month}-{d}'))
        Tracking.objects.bulk_create(objects_list)

        today_habits = Tracking.objects.filter(day=datetime.date.today(), habit__in=user_habits)
    return today_habits


class HabitsHome(LoginRequiredMixin, ListView):
    """Класс представления главной страницы с привычками на сегодня"""
    model = Tracking
    template_name = 'habits/index.html'
    login_url = '/login/'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today_habits'] = _get_today_habits(self.request.user.id)
        context['title'] = 'Главная страница'
        return context


class Statistic(LoginRequiredMixin, ListView):
    """Страница со статистикой привычек за месяц"""
    model = Tracking
    template_name = 'habits/statistic.html'
    login_url = '/login/'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_habits = Habits.objects.filter(user=self.request.user.id)
        context['month_habits'] = Tracking.objects.filter(
            day__gte=f'{datetime.datetime.now().year}-{datetime.datetime.now().month}-01',
            habit__in=user_habits
        ).order_by('habit_id')
        context['habits_list'] = Habits.objects.filter(user_id=self.request.user.id)
        context['days'] = list(range(1, monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1] + 1))
        context['title'] = 'Статистика привычек за месяц'
        return context


@login_required
def show_qr(request, habit_id):
    """Страница с отображением QR-кода привычки"""
    context = {'url': f'/media/qr_images/{habit_id}.jpg', 'title': 'QR-код привычки'}
    return render(request, 'habits/qr.html', context=context)


@login_required(login_url='/login/')
@require_http_methods(['POST'])
@csrf_exempt
def add(request):
    """Добавление новой привычки в БД"""
    _get_today_habits(request.user.id)
    name = request.POST['name']
    user_id = request.user.id
    habit = Habits(name=name, user_id=user_id)
    habit.save()
    objects_list = []
    for d in range(1, monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1] + 1):
        objects_list.append(Tracking(habit=habit, day=f'{datetime.datetime.now().year}-{datetime.datetime.now().month}-{d}'))
    Tracking.objects.bulk_create(objects_list)
    qr = qrcode.make(f'http://127.0.0.1:8000/update/{habit.id}/')
    qr.save(f'media/qr_images/{habit.id}.jpg', 'JPEG')
    habit.qr = f'qr_images/{habit.id}.jpg'
    habit.save()
    return redirect('index')


@login_required(login_url='/login/')
def update(request, habit_id):
    """Выполнение или отмена привычки"""
    habit = Tracking.objects.get(habit_id=habit_id, day=datetime.date.today())
    if request.user.id == habit.habit.user_id:
        habit.is_completed = not habit.is_completed
        habit.save()
    return redirect('index')


@login_required
def statistic_update(request, habit_id, day):
    """Выполнение или отмена привычки из страницы статистики"""
    habit = Tracking.objects.get(habit_id=habit_id,
                                 day=f'{datetime.datetime.now().year}-{datetime.datetime.now().month}-{day}')
    habit.is_completed = not habit.is_completed
    habit.save()
    return redirect('statistic')


@login_required
def delete(request, habit_id):
    """Удаление привычки и соотвествующего QR-кода из БД"""
    habit = Habits.objects.get(id=habit_id)
    os.remove(str(Path(__file__).resolve().parent.parent) + f'/media/qr_images/{habit_id}.jpg')
    habit.delete()
    return redirect('index')


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'habits/register.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('index')


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'habits/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        return context

    def get_success_url(self):
        return reverse_lazy('index')


def logout_user(request):
    logout(request)
    return redirect('login')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена<h1>')

