from django.forms import ModelForm
from .models import User


class UserLoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']
