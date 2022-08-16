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
    return redirect('index')


def update(request, habit_id):
    habit = Tracking.objects.get(id=habit_id)
    habit.is_completed = not habit.is_completed
    habit.save()
    return redirect('index')


def delete(request, habit_id):
    habit = Habits.objects.get(id=habit_id)
    habit.delete()
    return redirect('index')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена<h1>')
