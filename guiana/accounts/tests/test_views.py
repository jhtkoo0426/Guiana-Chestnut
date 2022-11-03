from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

CustomUser = get_user_model()


class AccountRegisterViewsTestClass(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(username="testuser", password="password", email="testuser@example.com")

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEquals(response.status_code, 200)
    
    def test_register_view_post_success(self):
        response = self.client.post(
            path=reverse('register'),
            data={
                'username': 'testuser2',
                'password': 'password',
                'password_2': 'password'
            },
        )
        self.assertRedirects(response, reverse('login'))
    
    # Add test for repeated username
    def test_register_view_post_existing_username(self):
        response = self.client.post(
            path=reverse('register'),
            data={
                'username': 'testuser',
                'password': 'password',
                'password_2': 'password'
            },
        )

        # We expect the view to display an error to the user, so the register page should not redirect.
        self.assertEquals(response.status_code, 200)

    def test_register_view_post_passwords_dont_match(self):
        response = self.client.post(
            path=reverse('register'),
            data={
                'username': 'testuser',
                'password': 'password',
                'password_2': 'password_2'
            },
        )

        # We expect the view to display an error to the user, so the register page should not redirect.
        self.assertEquals(response.status_code, 200)

    def test_register_template_used(self):
        response = self.client.get(reverse('register'))
        self.assertTemplateUsed(response, 'authentication/register.html')


class AccountLoginViewTestClass(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(username="testuser", password="password", email="testuser@example.com")

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)
    
    def test_login_view_post_success(self):
        response = self.client.post(
            path=reverse('login'),
            data={
                'username': 'testuser',
                'password': 'password'
            },
        )
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_login_view_post_failed(self):
        response = self.client.post(
            path=reverse('login'),
            data={
                'username': 'randomuser',
                'password': 'password'
            },
        )
        self.assertEquals(response.context['message'], "Login failed. Please enter the correct username or password.")

    def test_login_template_used(self):
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'authentication/login.html')
    

class AccountLogoutViewTestClass(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(username="testuser", password="password", email="testuser@example.com")
    
    def test_logout_view(self):
        self.client = Client()
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('logout'))
        self.assertEquals(response.status_code, 302)