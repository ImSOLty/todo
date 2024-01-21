import random

from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, TaskGroup, Tag
from .forms import TaskForm, TaskGroupForm
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
@require_http_methods(['GET'])
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
            if action == 'add':
                form = TaskGroupForm()
            elif action == 'edit':
                obj = TaskGroup.objects.get(id=target)
                form = TaskGroupForm(instance=obj)
    context = {'groups': TaskGroup.objects.filter(user=request.user), 'form': form, 'target': target, 'obj': obj,
               'form_type': form_type, 'tags': Tag.objects.filter(user=request.user),
               'uncompleted_tasks': Task.objects.filter(completed=False)}
    return render(request, 'base/tasks.html', context=context)


@login_required(login_url='login')
@require_http_methods(['POST'])
def create_task(request):
    form = TaskForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.group = TaskGroup.objects.get(id=request.POST.get('target'))
        task.user = request.user
        task.save()
    return redirect('home')


@login_required(login_url='login')
@require_http_methods(['POST'])
def update_task(request, pk):
    task = get_object_or_404(Task, id=pk)
    task.description = request.POST.get('description')
    task.title = request.POST.get('title')
    task.due = request.POST.get('due')
    task.completed = request.POST.get('completed') not in [None, 'False']
    task.save()
    return redirect('home')


@login_required(login_url='login')
@require_http_methods(['POST'])
def delete_task(request, pk):
    task = get_object_or_404(Task, id=pk)
    task.delete()
    return redirect('home')


@login_required(login_url='login')
@require_http_methods(['POST'])
def create_group(request):
    tag = Tag.objects.filter(title=request.POST.get('type_tag')).first()
    if tag is None:
        tag = Tag.objects.create(title=request.POST.get('type_tag'), user=request.user,
                                 color=('#%06X' % random.randint(0, 256 ** 3 - 1)))
    TaskGroup.objects.create(user=request.user, type_tag=tag,
                             description=request.POST.get('description'), title=request.POST.get('title'))
    return redirect('home')


@login_required(login_url='login')
@require_http_methods(['POST'])
def update_group(request, pk):
    tag = Tag.objects.filter(title=request.POST.get('type_tag')).first()
    if tag is None:
        tag = Tag.objects.create(title=request.POST.get('type_tag'), user=request.user,
                                 color=('#%06X' % random.randint(0, 256 ** 3 - 1)))
    group = get_object_or_404(TaskGroup, id=pk)
    group.description = request.POST.get('description')
    group.title = request.POST.get('title')
    group.type_tag = tag
    group.save()
    return redirect('home')


@login_required(login_url='login')
@require_http_methods(['POST'])
def delete_group(request, pk):
    group = get_object_or_404(TaskGroup, id=pk)
    group.delete()
    return redirect('home')
