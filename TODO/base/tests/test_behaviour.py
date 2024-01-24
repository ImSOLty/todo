from django.test import TestCase, Client
from users.models import User


class BehaviourTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user = User.objects.create_user(username="test", email='test@test.com', password='12345')
        self.client.login(username="test@test.com", password='12345')
