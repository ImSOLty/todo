from django.shortcuts import render, redirect
from django.http import Http404
from .models import Task, TaskGroup
from .forms import TaskForm


def home(request):
    form_type = request.GET.get('form_type')
    action = request.GET.get('action')
    form = None
    target = None
    obj = {'id': -1}
    if form_type is not None and action is not None:
        target = request.GET.get('target')
        if form_type == 'task':
            if action == 'add':
                form = TaskForm()
                target = TaskGroup.objects.get(id=target)
            elif action == 'edit':
                obj = Task.objects.get(id=target)
                target = obj.group
                form = TaskForm(instance=obj)
        elif form_type == 'group':
            pass
    context = {'groups': TaskGroup.objects.all(), 'form': form, 'target': target, 'obj': obj}
    return render(request, 'base/tasks.html', context=context)


def save_task(request, pk):
    task = Task.objects.filter(id=pk).first()
    if request.method == 'POST':
        if task is None:
            form = TaskForm(request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.group = TaskGroup.objects.get(id=request.POST.get('target'))
                task.user = request.user
        else:
            task.description = request.POST.get('description')
            task.title = request.POST.get('title')
            task.completed = request.POST.get('completed') is not None
        task.save()
    return redirect('home')


def delete_task(request, pk):
    if request.method == 'POST':
        task = Task.objects.get(id=pk)
        task.delete()
    return redirect('home')
