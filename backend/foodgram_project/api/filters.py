from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        recipes = Recipe.objects.all()
        if user.is_authenticated and value:
            return Recipe.objects.filter(favorites__user=user)
        return recipes

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        recipes = Recipe.objects.all()
        if user.is_authenticated and value:
            return Recipe.objects.filter(shopping__user=user)
        return recipes
