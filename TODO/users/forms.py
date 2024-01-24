from django.forms import ModelForm
from .models import User
from django.contrib.auth.forms import UserCreationForm


class UserLoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']
