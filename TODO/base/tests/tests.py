from django.test import TestCase, Client
from django.urls import reverse


class BasicTests(TestCase):

    def setUp(self):
        self.home_page = reverse('home')

    def test_homepage_status(self):
        self.client = Client()
        if self.client.get(self.home_page).status_code != 200:
            self.fail()
