from django.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField


# Create your models here.

class Template(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False)
    created = models.DateTimeField(auto_now_add=True, auto_created=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Tag(Template):
    color = ColorField()


class TaskGroup(Template):
    description = models.TextField(blank=True, null=True)
    tag = models.ManyToManyField(Tag)

    class Meta:
        ordering = ['title']


class Task(Template):
    group = models.ForeignKey(TaskGroup, on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['completed', 'title']
