from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/update/<str:pk>', views.update_task, name='update_task'),
    path('tasks/delete/<str:pk>', views.delete_task, name='delete_task'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/update/<str:pk>', views.update_group, name='update_group'),
    path('groups/delete/<str:pk>', views.delete_group, name='delete_group'),
]
