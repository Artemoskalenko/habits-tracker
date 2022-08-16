from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('add', add, name='add'),
    path('update/<int:habit_id>/', update, name='update'),
    path('delete/<int:habit_id>/', delete, name='delete')
]
