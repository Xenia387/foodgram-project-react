import django_filters
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from recipes.models import (
    Ingredient,
    Recipe,
)


class IngredientFilter(django_filters.FilterSet):
    """Фильтр ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""
    pass
