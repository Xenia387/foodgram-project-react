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


# https://stackoverflow.com/questions/47994336/django-filter-boolean-fields
# https://www.yourtodo.ru/posts/djangofilters-i-django-rest-framework/
# https://yandex.ru/search/?text=python+фильтрация+постов+по+добавленному+в+избранное&lr=2&clid=2323204&win=499
# https://dvmn.org/encyclopedia/django_orm/filter-start/
# https://stackoverflow.com/questions/47994336/django-filter-boolean-fields

# class RecipeFilter(django_filters.FilterSet):  # сделать или нет ??
class RecipeFilter(FilterSet):
    """Фильтр рецептов."""
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):  # убрать queryset и name ?
        user = self.request.user
        recipes = Recipe.objects.all()
        if user.is_authenticated and value:
            return Recipe.objects.filter(favorites__user=user)  # ??
        return recipes

    def filter_is_in_shopping_cart(self, querysey, name, value):
        user = self.request.user
        recipes = Recipe.objects.all()
        if user.is_authenticated and value:
            return Recipe.objects.filter(shopping_cart__user=user)  # ??
        return recipes
