from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, UserManager


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.user_type = 'super_admin'
        user.is_super_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    class Role:
        SUPER_ADMIN = 'super_admin'
        ADMIN = 'admin'
        CLIENT = 'client'

        choices = {
            (SUPER_ADMIN, 'super_admin'),
            (ADMIN, 'admin'),
            (CLIENT, 'client'),
        }
    email = models.EmailField('User Email', unique=True, null=False, blank=False)
    password = models.CharField('User Password', max_length=250)
    first_name = models.CharField('User Name', max_length=30, null=False, blank=True)
    last_name = models.CharField('User Last Name', max_length=50, null=False, blank=True)
    user_type = models.CharField('User Type', choices=Role.choices, max_length=12, default=Role.CLIENT, null=False, blank=False)
    company_id = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True, blank=False)
    avatar = models.FileField(upload_to='media/user_avatar', null=True, blank=False)
    telephone_number = PhoneNumberField(default='', null=False, blank=True, region='UA')

    is_active = models.BooleanField(default=True)
    is_super_admin = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_super_admin

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
