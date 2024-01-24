from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib import auth

from .. import views
from ..models import User
from ..forms import UserRegisterForm


class TestUsers(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_page = reverse('login')
        self.register_page = reverse('register')
        self.logout_page = reverse('logout')

    def create_user(self):
        data = {
            'email': 'test@test.com', 'first_name': 'Testname', 'last_name': 'Testsurname',
            'username': 'test', 'password1': 'UlTraUnU5ual'
        }
        data['password2'] = data['password1']
        data['password'] = data['password1']
        UserRegisterForm(data).save(commit=True)
        user = User.objects.get(email=data['email'])
        return user, data

    def create_and_login_user(self):
        user, data = self.create_user()
        self.client.login(username=data['email'], password=data['password1'])
        return user

    def test_resolve(self):
        self.assertEquals(resolve(self.login_page).func, views.login_user)
        self.assertEquals(resolve(self.register_page).func, views.register_user)
        self.assertEquals(resolve(self.logout_page).func, views.logout_user)

    def test_urls(self):
        for page in [self.login_page, self.register_page]:
            response = self.client.get(page)
            self.assertEquals(response.status_code, 200)
        self.assertEquals(self.client.get(self.logout_page).status_code, 405)

    def test_login_before_anything_else(self):
        response = self.client.get(reverse('home'))
        self.assertEquals(response.status_code, 302)
        if self.login_page not in str(response.url):
            self.fail()
        lst_post = [
            reverse('create_task', args=[]),
            reverse('update_task', args=[1]),
            reverse('delete_task', args=[1]),
            reverse('create_group', args=[]),
            reverse('update_group', args=[1]),
            reverse('delete_group', args=[1])
        ]
        for url in lst_post:
            response = self.client.post(url)
            self.assertEquals(response.status_code, 302)
            if self.login_page not in str(response.url):
                self.fail()

    def test_login_without_register(self):
        self.client.post(self.login_page, data={
            'email': 'test@test.com',
            'password': '12345',
        })
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_register_new_user(self):
        data = {
            'email': 'test@test.com',
            'first_name': 'Testname',
            'last_name': 'Testsurname',
            'password1': 'UlTraUnU5ual',
            'password2': 'UlTraUnU5ual',
        }
        self.client.post(self.register_page, data=data)

        user = User.objects.filter(email=data['email']).first()
        self.assertIsNotNone(user)
        for got, expected in [
            [user.email, data['email']],
            [user.first_name, data['first_name']],
            [user.last_name, data['last_name']],
        ]:
            self.assertEquals(got, expected)

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_register_with_already_used_email(self):
        data = {
            'email': 'test@test.com', 'first_name': 'Testname', 'last_name': 'Testsurname',
            'password1': 'UlTraUnU5ual', 'password2': 'UlTraUnU5ual',
        }
        UserRegisterForm(data).save(commit=True)
        self.client.post(self.register_page, data=data)

        data['first_name'] += '(UPD)'

        self.assertIsNone(User.objects.filter(first_name=data['first_name']).first())

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_login_user(self):
        self.create_and_login_user()

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_logout_user(self):
        self.create_and_login_user()

        response = self.client.post(self.logout_page)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, self.login_page)

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_login_incorrect_user(self):
        user, data = self.create_user()
        self.client.post(self.logout_page)

        for d in [
            {'email': data['email'] + '(UPD)', 'password': data['password']},
            {'email': data['email'], 'password': data['password'] + "(UPD)"},
            {'email': '', 'password': data['password']},
            {'email': data['email'], 'password': ''},
        ]:
            self.client.post(self.login_page, d)
            user = auth.get_user(self.client)
            self.assertFalse(user.is_authenticated)

    def test_logged_in_user_login_register_pages_redirect_to_home(self):
        self.create_and_login_user()

        for page in [self.login_page, self.register_page]:
            response = self.client.get(page)
            self.assertEquals(response.status_code, 302)
            self.assertEquals(response.url, reverse('home'))
