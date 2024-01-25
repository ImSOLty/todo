import random
import colorsys

from django.core.exceptions import FieldError
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, TaskGroup, Tag
from .forms import TaskForm, TaskGroupForm
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


def generate_random_color():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]
    return '#%02X%02X%02X' % (r, g, b)


@login_required(login_url='login')
@require_http_methods(['GET'])
def home(request):
    print(request)
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

    search = request.GET.get('q') if 'q' in request.GET.keys() else ''
    sorting = request.GET.get('sorted') if 'sorted' in request.GET.keys() else 'updated'
    tasks_of_search = Task.objects.filter(title__icontains=search)

    groups = TaskGroup.objects.filter(
        Q(user=request.user) & (Q(title__icontains=search) | Q(type_tag__title__icontains=search)
                                | Q(description__icontains=search) | Q(task__in=tasks_of_search))).distinct()
    try:
        groups = groups.order_by(sorting)
    except FieldError:
        sorting = 'updated'

    uncompleted_tasks = Task.objects.filter(Q(completed=False) & Q(user=request.user) & Q(group__in=groups))

    context = {'groups': groups, 'form': form, 'target': target, 'obj': obj,
               'form_type': form_type, 'tags': Tag.objects.filter(user=request.user),
               'uncompleted_tasks': uncompleted_tasks, 'search': search, 'sorting': sorting}
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
    tag = Tag.objects.filter(Q(title=request.POST.get('type_tag')) & Q(user=request.user)).first()
    if tag is None:
        tag = Tag.objects.create(title=request.POST.get('type_tag'), user=request.user,
                                 color=generate_random_color())
    TaskGroup.objects.create(user=request.user, type_tag=tag,
                             description=request.POST.get('description'), title=request.POST.get('title'))
    return redirect('home')


@login_required(login_url='login')
@require_http_methods(['POST'])
def update_group(request, pk):
    tag = Tag.objects.filter(Q(title=request.POST.get('type_tag')) & Q(user=request.user)).first()
    if tag is None:
        tag = Tag.objects.create(title=request.POST.get('type_tag'), user=request.user,
                                 color=generate_random_color())
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
