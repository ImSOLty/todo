from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tasks/save/<str:pk>', views.save_task, name='save_task'),
    path('tasks/delete/<str:pk>', views.delete_task, name='delete_task'),
]
