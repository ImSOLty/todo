from datetime import datetime

from django.db import models
from django.utils import timezone
from users.models import User
from colorfield.fields import ColorField


class Template(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False)
    created = models.DateTimeField(auto_now_add=True, auto_created=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Tag(Template):
    color = ColorField()

    class Meta:
        ordering = ['title']


class TaskGroup(Template):
    description = models.TextField(blank=True, null=True)
    type_tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        ordering = ['title']


class Task(Template):
    group = models.ForeignKey(TaskGroup, on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    due = models.DateField(blank=False, default=timezone.now)

    @property
    def remaining_days(self):
        return (self.due - datetime.today().date()).days

    class Meta:
        ordering = ['completed', 'due', 'title']
