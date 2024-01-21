import random

from django.test import TestCase, Client
from django.urls import reverse, resolve
from .. import views
from ..models import TaskGroup, Task, User, Tag
from .helper import random_color, random_str, random_data_task, random_data_taskgroup


class TestToDo(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_page = reverse('home')
        self.test_user = User.objects.create_user(username='test_user', password='12345')
        self.client.login(username='test_user', password='12345')
        self.test_tags = [Tag.objects.create(user=self.test_user, title=random_str(), color=random_color())
                          for _ in range(2)]
        self.test_groups = [TaskGroup.objects.create(
            user=self.test_user,
            title=random_str(),
            description=random_str(),
            type_tag=random.choice(self.test_tags)
        ) for _ in range(2)]

    def test_homepage_status(self):
        self.assertEquals(self.client.get(self.home_page).status_code, 200)
        self.assertNotEquals(self.client.post(self.home_page).status_code, 200)

    def test_list_url_is_resolved(self):
        urls = {
            reverse('home'): views.home,
            reverse('create_task', args=[]): views.create_task,
            reverse('update_task', args=[1]): views.update_task,
            reverse('delete_task', args=[1]): views.delete_task,
            reverse('create_group', args=[]): views.create_group,
            reverse('update_group', args=[1]): views.update_group,
            reverse('delete_group', args=[1]): views.delete_group
        }
        for url in urls.keys():
            self.assertIs(resolve(url).func, urls.get(url))

    def test_add_task_status(self):
        status_code = self.client.post(reverse('create_task'),
                                       random_data_task(target=random.choice(self.test_groups).id)).status_code
        self.assertEquals(status_code, 302, msg=f'{status_code}')
        self.assertNotEquals(self.client.get(reverse('create_task')).status_code, 200)

    def test_add_task_to_taskgroup(self):
        test_data = [random_data_task(target=random.choice(self.test_groups)) for _ in range(3)]

        for d in test_data:
            group = d['target']
            d['target'] = group.id

            self.client.post(reverse('create_task'), d)

            task = Task.objects.filter(title__icontains=d.get('title')).first()
            self.assertIsNotNone(task, msg=f'{d.get("title")}')

            for got, expected in [
                [task.title, d.get('title')],
                [task.description, d.get('description')],
                [task.completed, d.get('completed')],
                [task.due, d.get('due')],
                [task.group, group],
                [task.user, self.test_user],
            ]:
                self.assertEquals(got, expected)

    def test_edit_delete_task_in_taskgroup(self):
        data = [random_data_task(target=random.choice(self.test_groups)) for _ in range(3)]

        for d in data:
            group = d['target']
            d['target'] = group.id
            self.client.post(reverse('create_task'), d)
            task = Task.objects.filter(title__icontains=d.get('title')).first()

            changed_data = random_data_task(target=d['target'])

            status_code = self.client.post(reverse('update_task', args=[task.id]), changed_data).status_code
            self.assertEquals(status_code, 302)

            task = Task.objects.filter(id=task.id).first()
            self.assertIsNotNone(task)
            for got, expected in [
                [task.title, changed_data.get('title')],
                [task.description, changed_data.get('description')],
                [task.completed, changed_data.get('completed')],
                [task.due, changed_data.get('due')],
                [task.group, group],
                [task.user, self.test_user],
            ]:
                self.assertEquals(got, expected)

            self.assertEquals(self.client.post(reverse('delete_task', args=[-1])).status_code, 404)
            status_code = self.client.post(reverse('delete_task', args=[task.id])).status_code
            self.assertEquals(status_code, 302)
            self.assertIsNone(Task.objects.filter(id=task.id).first())

    def test_create_taskgroup_status(self):
        status_code = self.client.post(reverse('create_group'), random_data_taskgroup()).status_code
        self.assertEquals(status_code, 302)
        self.assertNotEquals(self.client.get(reverse('create_group')).status_code, 200)

    def test_create_taskgroup(self):
        data = [random_data_taskgroup(type_tag=random.choice(self.test_tags)) for _ in range(2)]
        for d in data:
            tag = d['type_tag']
            d['type_tag'] = tag.title
            self.client.post(reverse('create_group'), d)
            group = TaskGroup.objects.filter(title=d['title']).first()
            self.assertIsNotNone(group)
            for got, expected in [
                [group.title, d.get('title')],
                [group.description, d.get('description')],
                [group.type_tag, tag],
                [group.user, self.test_user],
            ]:
                self.assertEquals(got, expected)
            self.assertEquals(Task.objects.filter(group=group).count(), 0)

    def test_create_tag_while_creating_taskgroup(self):
        tags = [random_str() for _ in range(5)]
        colors = []
        for tag_title in tags:
            self.client.post(reverse('create_group'), random_data_taskgroup(type_tag=tag_title))
            tag = Tag.objects.filter(title=tag_title).first()
            self.assertIsNotNone(tag)
            colors.append(tag.color)
        self.assertEquals(len(set(colors)), len(tags))

    def test_update_delete_taskgroup(self):
        for group in self.test_groups:
            data = random_data_taskgroup(type_tag=random.choice(self.test_tags))
            tag = data['type_tag']
            data['type_tag'] = tag.title
            self.client.post(reverse('update_group', args=[group.id]), data)
            group = TaskGroup.objects.filter(id=group.id).first()
            self.assertIsNotNone(group)

            for got, expected in [
                [group.title, data.get('title')],
                [group.description, data.get('description')],
                [group.type_tag, tag],
                [group.user, self.test_user],
            ]:
                self.assertEquals(got, expected)
            self.assertEquals(Task.objects.filter(group=group).count(), 0)

    def test_create_tag_while_updating_taskgroup(self):
        tags = [random_str() for _ in range(5)]
        colors = []
        for tag_title in tags:
            group = random.choice(self.test_groups)
            self.client.post(reverse('update_group', args=[group.id]),
                             random_data_taskgroup(group=group.title, type_tag=tag_title))
            tag = Tag.objects.filter(title=tag_title).first()
            self.assertIsNotNone(tag)
            colors.append(tag.color)
        self.assertEquals(len(set(colors)), len(tags))

    def test_delete_taskgroup(self):
        for group in self.test_groups:
            self.assertEquals(self.client.post(reverse('delete_group', args=[-1])).status_code, 404)
            status_code = self.client.post(reverse('delete_group', args=[group.id])).status_code
            self.assertEquals(status_code, 302)
            self.assertIsNone(TaskGroup.objects.filter(id=group.id).first())
