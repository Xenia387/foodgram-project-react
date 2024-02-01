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

from users.models import (
    User,
    FIELD_EMAIL_MAX_LENGTH,
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
    TagRecipe,
    FIELDS_RECIPE_MODELS_MAX_LENGTH,
    FIELD_COLOR_MAX_LENGTH,
)


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

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class IngredientForRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиента из модели Ингредиент/Рецепт для создания
    Рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True, min_value=1)

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


class UserSignupSerializer(UserCreateSerializer):
    """Сериализатор регистрации."""
    email = serializers.EmailField(
        max_length=FIELD_EMAIL_MAX_LENGTH,
        required=True
    )
    username = serializers.CharField(
        max_length=FIELDS_USER_MAX_LENGTH,
        required=True
    )
    first_name = serializers.CharField(
        max_length=FIELDS_USER_MAX_LENGTH,
    )
    last_name = serializers.CharField(
        max_length=FIELDS_USER_MAX_LENGTH,
    )
    password = serializers.CharField(
        max_length=FIELDS_USER_MAX_LENGTH,
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

    def validate_username(self, value):
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
    ingredients = serializers.SerializerMethodField()
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

    def get_ingredients(self, recipe):
        """Ингредиенты рецепта."""
        return IngredientForRecipeReadOnlySerializer(
            IngredientRecipe.objects.filter(recipe=recipe).all(), many=True
        ).data


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания Рецепта."""
    ingredients = IngredientForRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()
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

    def validate_cooking_time(self, value):
        """Проверка поля время приготовления."""
        if value == 0:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше 1 минуты',
            )
        return value

    def validate_name(self, value):
        """Проверка поля навзания рецепта."""
        if len(value) >= 400:
            raise serializers.ValidationError(
                'Название в рецепте должно быть не длинее 400 символов',
            )
        return value

    def validate_ingredients(self, value):
        """Проверка поля ингредиенты."""
        if not value:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент',
            )
        return value

    def validate_tags(self, value):
        """Проверка поля теги."""
        if not value:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один тег',
            )
        return value

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.add(*tags)

        for ingredient in ingredients:
            id = ingredient.get('id')
            create_ingredient = ingredient.get('id')
            create_amount = ingredient.get('amount')
            IngredientRecipe.objects.create(
                ingredient=create_ingredient,
                amount=create_amount,
                recipe=recipe
            )

        return recipe

    def update(self, instance, validated_data):
        instance.ingredients = validated_data.get('ingredients', instance.ingredients)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.save()
        return instance


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


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписки на Пользователя."""
    user = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=CurrentUserDefault(),
    )
    author = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны',
            )
        ]

    def validate_author(self, value):
        if self.context.get('request').user == value:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя'
            )
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в избранное."""
    user = SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
        default=CurrentUserDefault(),
    )
    recipe = SlugRelatedField(
        slug_field='id',
        queryset=Recipe.objects.all(),
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное',
            )
        ]
