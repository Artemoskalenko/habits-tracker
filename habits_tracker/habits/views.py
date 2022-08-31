from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

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


def index(request):
    """Главная страница"""
    today_habits = get_today_habits()
    context = {'today_habits': today_habits, 'title': 'Главная страница'}
    return render(request, 'habits/index.html', context=context)


def statistic(request):
    """Страница со статистикой привычек за месяц"""
    month_habits = Tracking.objects.filter(
        day__gte=f'{datetime.datetime.now().year}-{datetime.datetime.now().month}-01').order_by('habit_id')
    habits_list = Habits.objects.all()
    days = list(range(1, monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]+1))
    context = {
        'month_habits': month_habits,
        'habits_list': habits_list,
        'days': days,
        'title': 'Статистика привычек за месяц'
    }
    return render(request, 'habits/statistic.html', context=context)


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
