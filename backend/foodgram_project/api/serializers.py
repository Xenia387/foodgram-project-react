import re
import base64
import webcolors
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.relations import SlugRelatedField

from recipes.models import (Favorite,
                            Follow,
                            Ingredient,
                            IngredientRecipe,
                            Recipe,
                            ShoppingList,
                            Tag,
                            )
from users.models import (User,
                          FIELD_EMAIL_MAX_LENGTH,
                          FIELDS_USER_MAX_LENGTH,
                          )


FIELD_RECIPE_NAME_MAX_LENGTH: int = 400


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        data = webcolors.hex_to_name(data)
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
    """Сериализатор Ингредиентов для сериализатора RecipeReadOnlySerializer.
    Только на чтение."""

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
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Тегов."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('__all__')


class UserAfterRegistSerializer(serializers.ModelSerializer):
    """Сериализатор Пользователя для вывода информации после регистрации.
    Только на чтение."""

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
        request = self.context.get('request')
        if (
            request.user.is_anonymous
            or request.user == obj.following.filter
            or not Follow.objects.filter(user=request.user, author=obj
                                         ).exists()
        ):
            return False
        if (
            request.user.is_authenticated
            and Follow.objects.filter(user=request.user, author=obj).exists()
        ):
            return True


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
            'username',
            'id',
            'first_name',
            'last_name',
            'password',
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                {'value': 'Имя пользователя не может быть "me"'},
            )
        invalid_chars_regex = re.compile(r'[^\w.@+-]+')
        invalid_chars = re.findall(invalid_chars_regex, value)
        if invalid_chars:
            raise serializers.ValidationError(
                {'value': 'Имя пользователя содержит недопустимые'
                 f'символы: {", ".join(invalid_chars)}'}
            )
        return value

    def validate(self, value):
        if User.objects.filter(email=value.get('email')).exists():
            user = User.objects.get(email=value.get('email'))
            raise serializers.ValidationError(
                {'value': 'Для этого email уже существует другой пользователь'}
                )
        if User.objects.filter(username=value.get('username')).exists():
            user = User.objects.get(username=value.get('username'))
            if user.email != value.get('email'):
                raise serializers.ValidationError(
                    {'value': 'Для этого пользователя указан другой email'}
                )
        return value

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return UserAfterRegistSerializer(instance, context=context).data


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор Рецепта. Только на чтение."""
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=False)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=False)
    image = Base64ImageField()

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

    def get_ingredients(self, obj):
        return IngredientForRecipeReadOnlySerializer(
            IngredientRecipe.objects.filter(recipe=obj).all(), many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if (
            request.user.is_anonymous
            or not Favorite.objects.filter(user=request.user, recipe=obj
                                           ).exists()
        ):
            return False
        if (
            request.user.is_authenticated
            and Favorite.objects.filter(user=request.user, recipe=obj).exists()
        ):
            return True

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if (
            request.user.is_anonymous
            or not ShoppingList.objects.filter(user=request.user, recipe=obj
                                               ).exists()
        ):
            return False
        if (
            request.user.is_authenticated
            and ShoppingList.objects.filter(user=request.user, recipe=obj
                                            ).exists()
        ):
            return True


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели связи между моделями Ингредиентов и Рецептов."""

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания Рецепта."""
    author = UserSerializer(read_only=True)
    ingredients = IngredientForRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, value):
        if value == 0:
            raise serializers.ValidationError(
                {'value': 'Время приготовления не может быть меньше 1 минуты'}
            )
        return value

    def validate_name(self, value):
        if len(value) >= FIELD_RECIPE_NAME_MAX_LENGTH:
            raise serializers.ValidationError(
                {'value':
                 'Название в рецепте должно быть не длинее 400 символов'}
            )
        return value

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                {'value': 'Рецепт должен содержать хотя бы один ингредиент'}
            )
        list_ingredient = []
        for ingredient in value:
            list_ingredient.append(ingredient['id'])
            if len(list_ingredient) != len(set(list_ingredient)):
                raise serializers.ValidationError(
                        {'value':
                         'Вы не можете добавить один ингредиент два раза'}
                    )
        return value

    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                {'value': 'Рецепт должен содержать хотя бы один тег'}
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                {'value': 'Вы не можете добавить один тег два раза'}
            )
        return value

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            create_ingredient = ingredient.get('id')
            create_amount = ingredient.get('amount')
            IngredientRecipe.objects.create(
                ingredient=create_ingredient,
                amount=create_amount,
                recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        instance.tags.set(tags)
        for ingredient in ingredients:
            create_ingredient = ingredient.get('id')
            create_amount = ingredient.get('amount')
            IngredientRecipe.objects.create(
                ingredient=create_ingredient,
                amount=create_amount,
                recipe=instance
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadOnlySerializer(instance, context=context).data


class UsersInSubscriptionSerializer(UserSerializer):
    """Сериализатор списка авторов, на которых подписан
    Пользователь и вывода информации об авторе после подписки.
    Только на чтение."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if (
            request.user.is_anonymous
            or request.user == obj.following.filter
            or not Follow.objects.filter(user=request.user, author=obj
                                         ).exists()
        ):
            return False
        if (
            request.user.is_authenticated
            and Follow.objects.filter(user=request.user, author=obj).exists()
        ):
            return True

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)
        if recipes_limit:
            recipes = recipes[:(int(recipes_limit))]
        return RecipeInFavoriteAndShopList(recipes, many=True).data

    def get_recipes_count(self, obj):
        count_recipes = Recipe.objects.filter(author=obj)
        return len(count_recipes)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор Подписки на Пользователя."""
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

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return UsersInSubscriptionSerializer(instance, context=context).data


class RecipeInFavoriteAndShopList(serializers.ModelSerializer):
    """Сериализатор вывода информации о Рецепте после
    добавления в Избранное и Список покупок. Только на чтение."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор добавления Рецепта в Список покупок."""

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
        return RecipeInFavoriteAndShopList(instance, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в Избранное."""
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

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeInFavoriteAndShopList(instance, context=context).data


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сериализатор изменения пароял."""
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')
