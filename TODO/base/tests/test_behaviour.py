from django.test import TestCase, Client
from ..models import User


class BehaviourTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user', password='test_password')
        self.client = Client()
        self.client.login(username='test_user', password='test_password')