from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email"""
    username = None  # Убираем поле username
    email = models.EmailField(unique=True, verbose_name='Электронная почта')

    # Дополнительные поля
    avatar = models.ImageField(
        upload_to='users/avatars/',
        verbose_name='Аватар',
        blank=True,
        null=True
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name='Номер телефона',
        blank=True,
        null=True
    )
    country = models.CharField(
        max_length=100,
        verbose_name='Страна',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'  # Авторизация по email
    REQUIRED_FIELDS = []  # Обязательные поля при создании суперпользователя

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email