from django.urls import path

from .views import *

urlpatterns = [
    path('', HabitsHome.as_view(), name='index'),
    path('statistic/', Statistic.as_view(), name='statistic'),
    path('statistic/<int:month>/', StatisticPrevious.as_view(), name='statistic_previous'),
    path('add/', add, name='add'),
    path('update/<int:habit_id>/', update, name='update'),
    path('delete/<int:habit_id>/', delete, name='delete'),
    path('show_qr/<int:habit_id>/', show_qr, name='show_qr'),
    path('statistic_update/<int:habit_id>/<int:day>/', statistic_update, name='statistic_update'),
    path('logout/', logout_user, name='logout'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register')
]
