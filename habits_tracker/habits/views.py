from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import qrcode
import datetime

from .models import *


def get_today_habits():
    today_habits = Tracking.objects.filter(day=datetime.date.today())
    if len(today_habits) == 0:
        for habit in Habits.objects.all():
            new_habit = Tracking(habit=habit, day=datetime.date.today())
            new_habit.save()
        today_habits = Tracking.objects.filter(day=datetime.date.today())
    return today_habits


def index(request):
    today_habits = get_today_habits()
    context = {'today_habits': today_habits, 'title': 'Главная страница'}
    return render(request,  'habits/index.html', context=context)


@require_http_methods(['POST'])
@csrf_exempt
def add(request):
    get_today_habits()
    name = request.POST['name']
    habit = Habits(name=name)
    habit.save()
    today_habit = Tracking(habit=habit, day=datetime.date.today())
    today_habit.save()
    qr = qrcode.make(f'http://127.0.0.1:8000/update/{today_habit.habit_id}/')
    qr.save(f'media/qr_images/{today_habit.habit_id}.jpg', 'JPEG')
    habit.qr = f'qr_images/{today_habit.habit_id}.jpg'
    print(habit.qr)
    habit.save()
    return redirect('index')


def show_qr(request, habit_id):
    url = f'/media/qr_images/{habit_id}.jpg'
    return render(request, 'habits/qr.html', {'url': url})


def update(request, habit_id):
    habit = Tracking.objects.get(habit_id=habit_id, day=datetime.date.today())
    habit.is_completed = not habit.is_completed
    habit.save()
    return redirect('index')


def delete(request, habit_id):
    habit = Habits.objects.get(id=habit_id)
    habit.delete()
    return redirect('index')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена<h1>')
