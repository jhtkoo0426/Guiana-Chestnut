from django.contrib.auth import get_user_model
from django.test import TestCase

CustomUser = get_user_model()


class AccountsTestClass(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="user1@gmail.com", username="user1", password="1234")

    def test_create_user(self):
        self.assertEqual(self.user.username, "user1")

    def test_user_active(self):
        self.assertTrue(self.user.is_active)
    
    def test_user_admin(self):
        self.assertFalse(self.user.is_admin)
    
    def test_user_str_class(self):
        self.assertEquals(str(self.user), "user1@gmail.com")
    
    def test_raises_error_if_user_no_username(self):
        with self.assertRaisesMessage(ValueError, "Users must have a username"):
            CustomUser.objects.create_user(email="user1@gmail.com",username=None, password="1234")
    
    def test_raises_error_if_user_no_email(self):
        with self.assertRaisesMessage(ValueError, "Users must have an email address"):
            CustomUser.objects.create_user(email="", username="user_no_email", password="1234")

    def test_raises_error_if_user_no_password(self):
        with self.assertRaisesMessage(ValueError, "Users must have a password"):
            CustomUser.objects.create_user(email="user1@gmail.com",username="user_no_pwd", password="")