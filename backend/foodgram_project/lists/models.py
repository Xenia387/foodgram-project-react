from django.db import models

from foodgram.models import (
    Ingredient,
    Recipe,
)
from users.models import CustomUser


class Favorite(models.Model):
    """Добавить Рецепт в избранное."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user_favorite',
        verbose_name='Вы',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_favorite',
        verbose_name='Рецепт',
        help_text='Вы можете добавить этот рецепт в избранное',
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return (f'Рецепт {self.recipe} был добавлен '
                f'в избранное пользователем {self.user}')


class Follow(models.Model):
    """Подписаться на Пользователя."""
    user = models.ForeignKey(
        CustomUser,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        help_text='Вы',
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автора',
        help_text='Вы можете подписаться на этого автора',
    )

    class Meta:
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (
            f'{self.user} подписан(а) на пользователя {self.author}'
        )


class ShoppingList(models.Model):
    """Корзина покупок"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shoppinglist',
        verbose_name='Вы',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppinglist',
        verbose_name='Рецепт в корзине',
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name_plural = 'Список покупок'
