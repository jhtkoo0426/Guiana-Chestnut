from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, username, phone=None, password=None, is_active=True, is_staff=False,
                    is_admin=False):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if not password:
            raise ValueError('Users must have a password')

        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            phone=phone,
        )

        user.set_password(password)
        user.staff = is_staff
        user.admin = is_admin
        user.active = is_active
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password, username):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            username,
            password=password,
            is_staff=True,
        )

        return user

    def create_superuser(self, email, password, username, phone):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            username,
            password=password,
            phone=phone,
            is_staff=True,
            is_admin=True,
        )

        return user


class CustomUser(AbstractUser):
    # User property fields
    username = models.CharField(max_length=50, blank=True, null=True, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True, unique=False)
    finnhub_api_key = models.CharField(max_length=100, blank=True, null=True, unique=True)

    # User type fields
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone']

    def __str__(self):
        return self.email

    # Inherited functions from AbstractBaseUser
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        # Is the user a member of staff?
        return self.staff

    @property
    def is_admin(self):
        # Is the user a admin member?
        return self.admin

    @property
    def is_active(self):
        return self.active