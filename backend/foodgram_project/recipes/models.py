from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import User

FIELDS_RECIPE_MODELS_MAX_LENGTH: int = 200
FIELD_COLOR_MAX_LENGTH: int = 16


class Tag(models.Model):
    """Тег"""
    name = models.CharField(
        max_length=FIELDS_RECIPE_MODELS_MAX_LENGTH,
        verbose_name='Тег',
    )
    color = models.CharField(max_length=FIELD_COLOR_MAX_LENGTH)
    slug = models.SlugField(
        unique=True,
        max_length=FIELDS_RECIPE_MODELS_MAX_LENGTH,
        verbose_name='Адрес тега',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиент"""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=FIELDS_RECIPE_MODELS_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        max_length=FIELDS_RECIPE_MODELS_MAX_LENGTH,
        verbose_name='Единица измерения',
    )
    amount = models.IntegerField()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор',
        help_text='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
        help_text='Необходимые ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        related_name='recipe',
        verbose_name='Тег',
        help_text='Тег, к которому будет относиться рецепт',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipe/',
        blank=True,
        help_text='Изображение',
    )
    name = models.TextField(
        max_length=FIELDS_RECIPE_MODELS_MAX_LENGTH,
        verbose_name='Название',
        help_text='Название',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Способ приготовления',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        null=False,
    )
    created = models.DateTimeField(
        'created',
        auto_now_add=True,
        help_text='Дата публикации',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Связь моделей Рецепта и Ингредиента"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient_in_recipe',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1000)
        ],
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты/Рецепты'

    def __str__(self):
        return (
            f'{self.ingredient.name} '
            f'{self.amount} '
            f'({self.ingredient.measurement_unit})'
        )


class TagRecipe(models.Model):
    """Связь моделей Рецепта и Тега"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tag',
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        related_name='tag_in_recipe',
        on_delete=models.CASCADE,
        verbose_name='Тег',
    )

    class Meta:
        verbose_name_plural = 'Теги/Рецепты'


class Favorite(models.Model):
    """Добавить Рецепт в избранное."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Вы',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
        help_text='Вы можете добавить этот рецепт в избранное',
    )

    class Meta:
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self):
        return (f'Рецепт {self.recipe} был добавлен '
                f'в избранное пользователем {self.user}')


class Follow(models.Model):
    """Подписаться на Пользователя."""
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        help_text='Вы',
    )
    author = models.ForeignKey(
        User,
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
    """Список покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppings',
        verbose_name='Вы',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='Рецепт в корзине',
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return (f'Рецепт {self.recipe} был добавлен '
                f'в список покупок пользователем {self.user}')
