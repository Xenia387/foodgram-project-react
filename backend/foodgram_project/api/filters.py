import django_filters
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from foodgram.models import (
    Ingredient,
    Recipe,
    Tag,
    CustomUser,
)
from lists.models import (
    Favorite,
    ShoppingList,
)


class IngredientFilter(django_filters.FilterSet):
    """Фильтр ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):  # вероятно падает потому что пользователь должен быть зарегестрирован
    """Фильтр рецептов."""
    # author = filters.ModelChoiceFilter(  # вроде работает и закомеченным 16:00
    #     field_name='author__username',  # username ошибка 500
    #     # to_field_name='username',
    #     # queryset=CustomUser.objects.all()
    # )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        # to_field_name='slug',
        # queryset=Tag.objects.all()
        )
    # tags = filters.AllValuesMultipleFilter(
    # # tags = django_filters.ModelMultipleChoiceFilter(  # вроде работает 16:00
    #     field_name='tags__slug',
    #     to_field_name='slug',
        # queryset=Tag.objects.all(),
    # )
    # is_favorited = filters.BooleanFilter(method='get_is_favorited')
    # is_in_shopping_cart = filters.BooleanFilter(
    #     method='get_is_in_shopping_cart'
    # )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    # def is_favorited_filter(self, queryset, name, value):
    #     user = self.request.user.pk
    #     if value:
    #         return queryset.filter(favorite__user=user)
    #     return queryset

    # def is_in_shopping_cart_filter(self, queryset, name, value):
    #     user = self.request.user.pk
    #     if value:
    #         return queryset.filter(shoppingcart__user=user)
    #     return queryset
