from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout, authenticate

from .models import User
from .forms import UserLoginForm


@require_http_methods(['POST', 'GET'])
def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    context = {'form': UserLoginForm()}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email).first()
        if user is None:
            return redirect('login')
        user = authenticate(request, email=email, password=password)
        if user is None:
            return redirect('login')
        login(request, user)
        return redirect('home')
    return render(request, 'users/login.html', context=context)


def logout_user(request):
    logout(request)
    return redirect('login')
