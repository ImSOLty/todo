from django.forms import ModelForm
from . import models


class TaskForm(ModelForm):
    class Meta:
        model = models.Task
        fields = '__all__'
        exclude = ['user', 'group']


class TaskGroupForm(ModelForm):
    class Meta:
        model = models.TaskGroup
        fields = '__all__'
        exclude = ['user']

