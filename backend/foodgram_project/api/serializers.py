import re
import base64
# import datetime as dt

import webcolors
from django.core.files.base import ContentFile

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.relations import SlugRelatedField
from djoser.serializers import UserCreateSerializer
# from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework.relations import PrimaryKeyRelatedField

from foodgram_project.settings import (
    EMAIL_MAX_LENGTH,
    FIELDS_USER_MAX_LENGTH,
)
from recipes.models import (
    Favorite,
    Follow,
    ShoppingList,
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag,
)
from users.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    """."""
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для страницы списка Ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientForRecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиентов для сериализатора RecipeReadOnlySerializer."""

    class Meta:
        model = Ingredient
        fields = ('__all__')

    # id = serializers.PrimaryKeyRelatedField(
    #     source='ingredient',
    #     queryset=Ingredient.objects.all()
    # )
    # name = serializers.StringRelatedField(
    #     source='ingredient.name'
    # )
    # measurement_unit = serializers.StringRelatedField(
    #     source='ingredient.measurement_unit'
    # )

    # class Meta:
    #     model = IngredientRecipe
    #     fields = ('amount', 'name', 'measurement_unit', 'id')


class IngredientForRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиента из модели Ингредиент/Рецепт для создания
    Рецепта."""
    # recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    # id = serializers.PrimaryKeyRelatedField(
    #     source='ingredient',
    #     # source='ingredient_in_recipe',
    #     queryset=Ingredient.objects.all()
    # )
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = IngredientRecipe
        fields = (
            # 'recipe',
            'id',
            'amount'
        )


class IngredientsAmountInShoppingCart(serializers.ModelSerializer):
    """Подсчёт количества Ингредиентов в Списке покупок."""

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Тегов."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('__all__')


class UserAfterRegistSerializer(serializers.ModelSerializer):
    """Вывод информации о Пользователе после регистрации."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор Пользователя для страниц:
    Список пользователей, Профиль пользоваетеля,
    Текущий пользователь. Только на чтение."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user == obj.following.filter:
            return False
        return bool(
            user.is_authenticated
            and obj.following.filter(user=user).exists()
        )


# class UserProfileSerializer(serializers.ModelSerializer):
#     """Сериализатор Пользователя для страниц:
#     Профиль пользоваетеля. Только на чтение."""
#     is_subscribed = serializers.SerializerMethodField(read_only=True)
#     recipes = RecipeReadOnlySerializer(read_only=True)

#     class Meta:
#         model = CustomUser
#         fields = (
#             'email',
#             'id',
#             'username',
#             'first_name',
#             'last_name',
#             'is_subscribed',
#         )

#     def get_is_subscribed(self, obj):
#         user = self.context.get('request').user
#         if user == obj.following.filter:
#             return False
#         return bool(
#             user.is_authenticated
#             and obj.following.filter(user=user).exists()
#         )

# class UserRecieveTokenSerializer(serializers.Serializer):

#     email = serializers.EmailField(
#         max_length=EMAIL_MAX_LENGTH,
#         required=True
#     )

#     password = serializers.CharField(
#         max_length=150,
#     )

#     class Meta:
#         model = CustomUser
#         fields = (
#             'password',
#             'email',
#         )


class UserSignupSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации."""
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True
    )
    username = serializers.CharField(
        max_length=150,
        required=True
    )
    first_name = serializers.CharField(
        max_length=150,
    )
    last_name = serializers.CharField(
        max_length=150,
    )
    password = serializers.CharField(
        max_length=150,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate_username(value):
        """
        Валидация запрета недопустимых символов
        """
        invalid_chars_regex = re.compile(r'[^\w.@+-]+')
        invalid_chars = re.findall(invalid_chars_regex, value)
        if invalid_chars:
            raise serializers.ValidationError(
                'Имя пользователя содержит недопустимые'
                f'символы: {", ".join(invalid_chars)}',
            )
        if not re.match(UnicodeUsernameValidator.regex, value):
            raise serializers.ValidationError(
                UnicodeUsernameValidator.message
            )
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть "me".',
            )
        return value

    def validate_email(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                f'Нельзя использовать email "{value}".'
            )
        if not re.match(UnicodeUsernameValidator.regex, value):
            raise serializers.ValidationError(
                UnicodeUsernameValidator.message
            )
        return value

    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            user = User.objects.get(email=data['email'])
            if user.username != data['username']:
                raise serializers.ValidationError(
                    'Для этого email уже существует другой пользователь'
                )
        if User.objects.filter(username=data['username']).exists():
            user = User.objects.get(username=data['username'])
            if user.email != data['email']:
                raise serializers.ValidationError(
                    'Для этого пользователя указан другой email'
                )
        return data


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор Рецепта. Только на чтение."""
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientForRecipeReadOnlySerializer(many=True)
    # ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=False)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=False)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    # def get_ingredients(self, obj):
    #     return IngredientForRecipeReadOnlySerializer(
    #         IngredientRecipe.objects.filter(recipe=obj).all(), many=True
    #     ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели связи между моделями Ингредиентов и Рецептов."""
    # name = 

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания Рецепта."""
    tags = PrimaryKeyRelatedField(many=True, read_only=True)
    # ingredients = IngredientRecipeSerializer(many=True)
    ingredients = IngredientForRecipeCreateSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, value):
        ingredinets = value.get('ingredinets')
        tags = value.get('tags')
        image = value.get('image')
        cooking_time = value.get('cooking_time')

        if not image or not cooking_time:
            raise ValueError('Не забудьте загрузить изображение и указать '
                             'время пригтоовления.')
        if not ingredinets or not tags:
            raise ValueError('Необходимо добавить хотя бы '
                             'один игредиент и тег.')
        return value

    def ingredients_add(self, validated_data):
        pass

        def create(self, validated_data):
            author = self.context.get('request').user
            ingredients = validated_data.pop('ingredients')
            tags = validated_data.pop('tags')
            recipe = Recipe.objects.create(**validated_data)
            recipe.tags.set(tags)
            self.create_ingredients_amounts(recipe=recipe, author=author)
            return recipe

    # def create(self, validated_data):
    #     ingredients = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(**validated_data)
    #     recipe.tags.set(tags)
    #     self.create_ingredients_amounts(recipe=recipe, ingredients=ingredients)
    #     return recipe


class RecipeInFavoriteAndShopList(serializers.ModelSerializer):
    """Сериализатор вывода информации о рецепте после
    добавления в избранное и список покупок. Только на чтение."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта в Список покупок."""

    user = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )
    recipe = SlugRelatedField(
        slug_field='name',
        queryset=Recipe.objects.all(),
    )

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок',
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeInFavoriteAndShopList(instance.recipe, context=context).data


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписки на Пользователя."""
    user = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=CurrentUserDefault(),
    )
    following = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны',
            )
        ]

    def validate_following(self, value):
        if self.context.get('request').user == value:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя'
            )
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в избранное."""
    user = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=CurrentUserDefault(),
    )
    recipe = SlugRelatedField(
        slug_field='name',
        queryset=Recipe.objects.all(),
    )

    class Meta:
        model = Follow
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное',
            )
        ]

    # def to_representation(self, instance):
    #     request = self.context.get('request')
    #     return RecipeInFav3oriteAndSubcribe(
    #         instance.recipe, context={'request': request}
    #     ).data


class ChangePasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ('current_password', 'new_password')


class UsersInSubscriptionSerializer(UserSerializer):
    """Сериализатор списка авторов, на которых подписан
    пользователь. Только на чтение."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    # class Meta:
    #     model = User
    #     fields = (
    #         'email',
    #         'id',
    #         'username',
    #         'first_name',
    #         'last_name',
    #         'is_subscribed',
    #         'recipes',
    #         'recipes_count'
    #     )
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return bool(
            user.is_authenticated
            and obj.following.filter(user=user).exists()
        )

    def get_recipes(self, obj):
        pass

    def get_recipes_count(self, obj):
        return obj.recipes.count()
