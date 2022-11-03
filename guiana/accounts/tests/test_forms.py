from django.contrib.auth import get_user_model
from django.test import TestCase
from accounts.forms import UserAdminCreationForm, UserLoginForm, UserRegisterForm

CustomUser = get_user_model()


class UserRegisterFormTestClass(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(username="testuser", password="testuser", email="testuser@example.com")

    def test_register_form_is_valid(self):
        form_data = {
            "username": "testuser2", 
            "password": "testuser", 
            "password_2": "testuser",
        }

        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_register_form_raises_error_if_invalid_username(self):
        form_data = {
            "username": "",
            "password": "password",
            "password_2": "password"
        }

        form = UserRegisterForm(data=form_data)
        self.assertFormError(
            form=form,
            field='username',
            errors=['This field is required.']
        )
    
    def test_register_form_raises_error_if_taken_username(self):
        # A user with the username "testuser" was created during setUp. So, we expect
        # the form to raise an error.
        form_data = {
            "username": "testuser", 
            "password": "testuser", 
            "password_2": "testuser"
        }

        form = UserRegisterForm(data=form_data)
        self.assertFormError(
            form=form,
            field='username',
            errors=['This username has been taken. Please try a different username!']
        )
    
    def test_register_form_raises_error_if_no_validation_password(self):
        form_data = {
            "username": "testuser3", 
            "password": "testuser", 
            "password_2": ""
        }

        form = UserRegisterForm(data=form_data)
        self.assertFormError(
            form=form,
            field='password_2',
            errors=['This field is required.']
        )

    def test_register_form_raises_error_if_passwords_dont_match(self):
        form_data = {
            "username": "testuser4",
            "password": "password",
            "password_2": "1234"
        }

        form = UserRegisterForm(data=form_data)
        self.assertEquals(form.errors['__all__'][0], 'Your passwords must match. Please try again!')


class UserLoginFormTestClass(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(username="testuser", password="password", email="testuser@example.com")
        
        self.credentials = {
            "username": "testuser",
            "password": "password",
        }
        
    def test_login_form_is_valid(self):
        logged_in = self.client.login(username="testuser", password="password")
        self.assertTrue(logged_in)
    
    def test_login_redirect(self):
        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
    
    def test_login_form_is_invalid_if_invalid_username(self):
        form_data = {
            "username": "randomusername",
            "password": "password"
        }

        form = UserLoginForm(data=form_data)
        self.assertEquals(form.errors['__all__'][0], 'Invalid username or password. Please try again.')
    
    def test_login_form_is_invalid_if_no_username(self):
        form_data = {
            "username": "",
            "password": "password"
        }

        form = UserLoginForm(data=form_data)
        self.assertEquals(form.errors['__all__'][0], 'Invalid username or password. Please try again.')
    
    def test_login_form_is_invalid_if_invalid_password(self):
        form_data = {
            "username": "testuser",
            "password": "randompassword"
        }

        form = UserLoginForm(data=form_data)
        self.assertEquals(form.errors['__all__'][0], 'Invalid username or password. Please try again.')


class UserAdminCreationFormTestClass(TestCase):

    def setUp(self):
        CustomUser.objects.create_superuser(username="testsuperuser", password="password", email="testadmin@example.com")
    
    def test_admin_creation_form_is_valid(self):
        form_data = {
            "username": "testsuperuser2",
            "password": "password",
            "password_2": "password"
        }

        form = UserAdminCreationForm(data=form_data)
        form.save()
        self.assertTrue(form.is_valid())
    
    def test_admin_creation_form_raise_error_if_invalid_username(self):
        form_data = {
            "username": "",
            "password": "password",
            "password_2": "password"
        }

        form = UserAdminCreationForm(data=form_data)
        self.assertFormError(
            form=form,
            field='username',
            errors=['This field is required.']
        )
    
    def test_admin_creation_form_raises_error_if_taken_username(self):
        # A user with the username "testuser" was created during setUp. So, we expect
        # the form to raise an error.
        form_data = {
            "username": "testsuperuser", 
            "password": "password", 
            "password_2": "password"
        }

        form = UserAdminCreationForm(data=form_data)
        self.assertFormError(
            form=form,
            field='username',
            errors=['This username has been taken. Please try a different username!']
        )
    
    def test_admin_creation_form_raises_error_if_no_validation_password(self):
        form_data = {
            "username": "testsuperuser", 
            "password": "password", 
            "password_2": ""
        }

        form = UserAdminCreationForm(data=form_data)
        self.assertFormError(
            form=form,
            field='password_2',
            errors=['This field is required.']
        )

    def test_admin_creation_form_raises_error_if_passwords_dont_match(self):
        form_data = {
            "username": "testsuperuser3",
            "password": "password",
            "password_2": "1234"
        }

        form = UserAdminCreationForm(data=form_data)
        self.assertEquals(form.errors['__all__'][0], 'Your passwords must match.')