from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator

from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    phonenumber = PhoneNumberField(
        'Номер телефона пользователя',
        region='RU',
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Warehouse(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=100
    )
    contact_phone = PhoneNumberField(
        'Контактный телефон',
        max_length=50,
        blank=True
    )
    description = models.TextField(
        'Описание',
        max_length=200,
        blank=True
    )
    feature = models.CharField(
        'Особенность',
        max_length=100,
        blank=True
    )
    temperature = models.IntegerField(
        'Температура',
        blank=True
    )
    ceiling_height = models.DecimalField(
        'Высота потолка',
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(1)]
    )
    total_storages = models.IntegerField(
        'Всего хранилищ',
        blank=True,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

    def __str__(self):
        return self.address


