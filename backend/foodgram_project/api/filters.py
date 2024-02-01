import django_filters
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    User,
    Favorite,
    ShoppingList,
)
from users.models import User


class IngredientFilter(django_filters.FilterSet):
    """Фильтр ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""
    author = filters.ModelChoiceFilter(
        field_name='author__username',
        queryset=User.objects.all()
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
