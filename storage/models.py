from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator
from django.db.models.functions import Concat
from django.db.models import Count, F, Min, Value, Subquery, OuterRef, CharField

from phonenumber_field.modelfields import PhoneNumberField


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


class WarehouseManager(models.Manager):
    def with_annotations(self):
        return self.prefetch_related('storages__storage_type').annotate(
            total_storages=Count('storages'),
            min_price=Min('storages__storage_type__price')
        )


class Warehouse(models.Model):
    city = models.CharField(
        'Город',
        max_length=100
    )
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

    objects = WarehouseManager()

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

    def __str__(self):
        return f'{self.city}, {self.address}'


class StorageType(models.Model):
    length = models.DecimalField(
        'Длина',
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0)]
    )
    width = models.DecimalField(
        'Ширина',
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0)]
    )
    height = models.DecimalField(
        'Высота',
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0)]
    )
    price = models.IntegerField(
        'Цена',
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Тип хранилища'
        verbose_name_plural = 'Типы хранилищ'

    def __str__(self):
        return f'{self.length} х {self.width} х {self.height} м'

    def get_area(self):
        return self.length * self.width


class StorageManager(models.Manager):
    def with_characteristics(self):
        return self.prefetch_related('storage_type').annotate(
            area=F('storage_type__length') * F('storage_type__width'),
            size=Concat(
                F('storage_type__length'),
                Value(' x '),
                F('storage_type__width'),
                Value(' x '),
                F('storage_type__height'),
                output_field=CharField()
            ),
            price=F('storage_type__price')
        )


class Storage(models.Model):
    floor = models.IntegerField(
        'Этаж',
        validators=[MinValueValidator(1)]
    )
    number = models.CharField(
        'Номер хранилища',
        max_length=100
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='storages',
        verbose_name='Склад',
    )
    storage_type = models.ForeignKey(
        StorageType,
        on_delete=models.CASCADE,
        related_name='storages',
        verbose_name='Тип хранилища',
    )

    objects = StorageManager()

    class Meta:
        verbose_name = 'Хранилище'
        verbose_name_plural = 'Хранилища'

    def __str__(self):
        return self.number


class UserStorage(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Владелец',
        related_name='storages',
        on_delete=models.CASCADE
    )
    storage = models.OneToOneField(
        Storage,
        verbose_name='Хранилище',
        related_name='rented_storage',
        on_delete=models.CASCADE
    )
    rent_start = models.DateTimeField('Дата начала аренды')
    rent_end = models.DateTimeField('Дата окончания аренды')
    paid = models.BooleanField('Оплачено', default=False)

    class Meta:
        verbose_name = 'Арендованное хранилище'
        verbose_name_plural = 'Арендованные хранилища'

    def __str__(self):
        return f'{self.user} {self.storage}'


def storages_with_address(user_storages):
    return user_storages.prefetch_related('storage').annotate(
        address=Concat(
            F('storage__warehouse__city'), 
            Value(', '), 
            F('storage__warehouse__address')
        )
    )
