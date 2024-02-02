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

# https://stackoverflow.com/questions/47994336/django-filter-boolean-fields
# https://www.yourtodo.ru/posts/djangofilters-i-django-rest-framework/
# https://yandex.ru/search/?text=python+фильтрация+постов+по+добавленному+в+избранное&lr=2&clid=2323204&win=499
class RecipeFilter(FilterSet):
    """Фильтр рецептов."""
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)
