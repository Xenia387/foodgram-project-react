from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram_project.settings import (
    EMAIL_MAX_LENGTH
)


class CustomUser(AbstractUser):
    """Переопределённая модель пользователя"""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username', 'first_name', 'last_name',
        # 'password'
    ]
    # password = models.CharField(
    #     max_length=150,
    #     verbose_name='password',
    # )
    email = models.EmailField(
        unique=True,
        db_index=True,
        max_length=EMAIL_MAX_LENGTH,
        verbose_name='email',
    )
    username = models.CharField(
        unique=True,
        db_index=True,
        max_length=150,
        verbose_name='Логин',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        # return '%s %s' % (self.first_name, self.last_name)
        return self.username

    # def is_subscribed(self):
    #     """Подписан ли кто-то на пользователя."""
    #     if self.following.all():
    #         return True
    #     else:
    #         return False
