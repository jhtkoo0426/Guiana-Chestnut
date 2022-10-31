from django.contrib.auth.models import (AbstractUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


class UserManager(BaseUserManager):
    def create_superuser(self, username, email, first_name, password=None, is_admin=True):
        """
        Creates and saves a superuser instance with the given username and password.
        """

        user = self.create_user(
            username=username,
            email=email,
            first_name=first_name,
            password=password,
        )

        user.is_admin = is_admin

        return user
    
    def create_user(self, username, email, first_name, password=None):
        """
        Creates and saves a basic user isntance with the given username and password.
        """

        if not username:
            raise ValueError("Users must have a username!")
    
        if not email:
            raise ValueError("Users must have an email address!")
        
        if not password:
            raise ValueError("Users must have a password!")
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    

class CustomUser(AbstractUser, PermissionsMixin):
    """
    An abstract base class implementing a User model.
    """

    username = models.CharField(max_length=50, blank=False, null=True, unique=True)
    email = models.EmailField(blank=False, null=True, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    finnhub_api_key = models.CharField(max_length=100, blank=True, null=True, unique=True)

    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name']

    def __str__(self):
        return self.username