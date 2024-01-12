from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
# from colorfield.fields import ColorField
# from django.core.exceptions import FieldDoesNotExist

# from django.conf import settings
from users.models import CustomUser


class Tag(models.Model):
    """Тег"""
    name = models.CharField(
        max_length=200,
        verbose_name='Тег',
    )
    color = models.CharField(max_length=16)
    # color = ColorField(
    #     format='hex',
    #     default='#FF0000',
    #     max_length=7,
    #     verbose_name='Цветовой HEX-код',
    #     help_text='Цветовой HEX-код',
    # )
    slug = models.SlugField(
        unique=True,
        max_length=200,
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
        max_length=200,
    )
    measurement_unit = models.CharField(
        max_length=200,
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
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор',
        help_text='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Необходимые ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        # null=True,
        # on_delete=models.SET_NULL,
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
        max_length=200,
        verbose_name='Название',
        help_text='Название',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Способ приготовления',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
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
        # related_name='amount_ingredients',
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
