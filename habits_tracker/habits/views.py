from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView,DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

import qrcode
import datetime
from calendar import monthrange
import os
from pathlib import Path

from .models import *


def get_today_habits():
    """Получение привычек на день"""
    today_habits = Tracking.objects.filter(day=datetime.date.today())
    if len(today_habits) == 0:
        objects_list = []
        for d in range(1, monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]+1):
            for habit in Habits.objects.all():
                objects_list.append(Tracking(habit=habit,
                                             day=f'{datetime.datetime.now().year}-{datetime.datetime.now().month}-{d}'))
        Tracking.objects.bulk_create(objects_list)

        today_habits = Tracking.objects.filter(day=datetime.date.today())
    return today_habits


class HabitsHome(ListView):
    """Класс представления главной страницы с привычками на сегодня"""
    model = Tracking
    template_name = 'habits/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today_habits'] = get_today_habits()
        context['title'] = 'Главная страница'
        return context


class Statistic(ListView):
    """Страница со статистикой привычек за месяц"""
    model = Tracking
    template_name = 'habits/statistic.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['month_habits'] = Tracking.objects.filter(
            day__gte=f'{datetime.datetime.now().year}-{datetime.datetime.now().month}-01').order_by('habit_id')
        context['habits_list'] = Habits.objects.all()
        context['days'] = list(range(1, monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1] + 1))
        context['title'] = 'Статистика привычек за месяц'
        return context


def show_qr(request, habit_id):
    """Страница с отображением QR-кода привычки"""
    context = {'url': f'/media/qr_images/{habit_id}.jpg', 'title': 'QR-код привычки'}
    return render(request, 'habits/qr.html', context=context)


@require_http_methods(['POST'])
@csrf_exempt
def add(request):
    """Добавление новой привычки в БД"""
    get_today_habits()
    name = request.POST['name']
    habit = Habits(name=name)
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


def update(request, habit_id):
    """Выполнение или отмена привычки"""
    habit = Tracking.objects.get(habit_id=habit_id, day=datetime.date.today())
    habit.is_completed = not habit.is_completed
    habit.save()
    return redirect('index')


def statistic_update(request, habit_id, day):
    """Выполнение или отмена привычки из страницы статистики"""
    habit = Tracking.objects.get(habit_id=habit_id,
                                 day=f'{datetime.datetime.now().year}-{datetime.datetime.now().month}-{day}')
    habit.is_completed = not habit.is_completed
    habit.save()
    return redirect('statistic')


def delete(request, habit_id):
    """Удаление привычки и соотвествующего QR-кода из БД"""
    habit = Habits.objects.get(id=habit_id)
    os.remove(str(Path(__file__).resolve().parent.parent) + f'/media/qr_images/{habit_id}.jpg')
    habit.delete()
    return redirect('index')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена<h1>')


# class RegisterUser(DataMixin, CreateView):