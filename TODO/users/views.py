from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from .models import User
from .forms import UserLoginForm, UserRegisterForm


@require_http_methods(['POST', 'GET'])
def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    context = {'page': 'login', 'form': UserLoginForm()}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email).first()
        if user is None:
            messages.error(request, "Incorrect credentials!")
            return redirect('login')
        user = authenticate(request, email=email, password=password)
        if user is None:
            messages.error(request, "Incorrect credentials!")
            return redirect('login')
        login(request, user)
        return redirect('home')
    return render(request, 'users/login_register.html', context=context)


@require_http_methods(['POST', 'GET'])
def register_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = UserRegisterForm()
    context = {'page': 'register', 'form': form}
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.username = user.email
            user.first_name = user.first_name.capitalize()
            user.last_name = user.last_name.capitalize()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            for message in form.errors.values():
                messages.error(request, message)
            return redirect('register')

    return render(request, 'users/login_register.html', context=context)


@require_http_methods(['POST'])
def logout_user(request):
    logout(request)
    return redirect('login')


@require_http_methods(['GET', 'POST'])
def settings(request):
    context = {}
    user = request.user
    avatar_file = request.FILES['avatar'] if 'avatar' in request.FILES.keys() else request.user.avatar
    background_file = request.FILES['background'] if 'background' in request.FILES.keys() else request.user.background
    if request.method == 'POST':
        if request.POST.get('password1') or request.POST.get('password2'):
            form = UserRegisterForm(instance=user, data=request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.email = user.email.lower()
                user.avatar = avatar_file
                user.background = background_file
                user.save()
                login(request, user)
        else:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email').lower()
            user.avatar = avatar_file
            user.background = background_file
            user.save()
    return render(request, 'users/settings.html', context=context)
