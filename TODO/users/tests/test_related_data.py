import random
from datetime import datetime, timedelta

from django.db.models import Q
from django.test import TestCase, Client
from django.contrib import auth
from django.urls import reverse

from ..forms import UserRegisterForm

from base.models import TaskGroup, Task, Tag


def create_and_login_client(data):
    client = Client()
    client.post(reverse('register'), data=data)
    client.login(username=data['email'], password=data['password1'])
    return client


class TestRelatedData(TestCase):

    def setUp(self):
        self.client1 = create_and_login_client(
            {'email': 'test1@test.com', 'username': 'test1', 'password1': 'sdf7aas8d2n3', 'password2': 'sdf7aas8d2n3'})
        self.client2 = create_and_login_client(
            {'email': 'test2@test.com', 'username': 'test2', 'password1': 'aknsgl23gh89', 'password2': 'aknsgl23gh89'})

    def test_users_existence(self):
        for client in [self.client1, self.client2]:
            user = auth.get_user(client)
            self.assertIsNotNone(user)
            self.assertTrue(user.is_authenticated)

    def test_objects_only_related_to_user(self):
        data1 = [
            {'user': 1, 'group': 'Test1', 'tag': 'test_tag1', 'task': '1_1_test_task'},
            {'user': 1, 'group': 'Test1', 'tag': 'test_tag1', 'task': '1_2_test_task'},
            {'user': 1, 'group': 'Test2', 'tag': 'test_tag2', 'task': '1_3_test_task'},
            {'user': 1, 'group': 'Test2', 'tag': 'test_tag2', 'task': '1_4_test_task'}
        ]
        data2 = [
            {'user': 2, 'group': 'Test3', 'tag': 'test_tag3', 'task': '1_5_test_task'},
            {'user': 2, 'group': 'Test3', 'tag': 'test_tag3', 'task': '1_6_test_task'},
            {'user': 2, 'group': 'Test4', 'tag': 'test_tag4', 'task': '1_7_test_task'},
            {'user': 2, 'group': 'Test4', 'tag': 'test_tag4', 'task': '1_8_test_task'},
        ]
        for d in data1 + data2:
            active_client = self.client1 if d['user'] == 1 else self.client2
            user = auth.get_user(active_client)
            group = TaskGroup.objects.filter(Q(title=d['group']) & Q(user=user)).first()
            if group is None:
                active_client.post(reverse('create_group'), data={
                    'title': d['group'],
                    'type_tag': d['tag']
                })
            group = TaskGroup.objects.filter(Q(title=d['group']) & Q(user=user)).first()
            active_client.post(reverse('create_task'), data={
                'title': d['task'],
                'due': (datetime.today() + timedelta(days=random.randint(0, 20))).date(),
                'target': group.id
            })
        # TODO
