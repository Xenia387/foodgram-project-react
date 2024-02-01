from django.contrib.auth.models import AbstractUser
from django.db import models

FIELDS_USER_MAX_LENGTH: int = 150
FIELD_EMAIL_MAX_LENGTH: int = 254


class User(AbstractUser):
    """Переопределённая модель пользователя"""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(
        unique=True,
        db_index=True,
        max_length=FIELD_EMAIL_MAX_LENGTH,
        verbose_name='email',
    )
    username = models.CharField(
        unique=True,
        db_index=True,
        max_length=FIELDS_USER_MAX_LENGTH,
        verbose_name='Логин',
    )
    first_name = models.CharField(
        max_length=FIELDS_USER_MAX_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=FIELDS_USER_MAX_LENGTH,
        verbose_name='Фамилия',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)
