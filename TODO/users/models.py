from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    avatar = models.FileField(default='images/placeholder-avatar.jpg', upload_to='media')
    background = models.FileField(default='images/placeholder-background.png', upload_to='media')
    first_name = models.CharField(default='No', blank=False, max_length=200)
    last_name = models.CharField(default='Name', blank=False, max_length=200)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
