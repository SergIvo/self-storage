# Generated by Django 4.2 on 2023-04-20 11:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0002_storage_warehouse_alter_user_phonenumber_userstorage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storage',
            name='height',
            field=models.DecimalField(decimal_places=1, max_digits=2, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Высота'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='length',
            field=models.DecimalField(decimal_places=1, max_digits=3, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Длина'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='width',
            field=models.DecimalField(decimal_places=1, max_digits=3, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Ширина'),
        ),
    ]
