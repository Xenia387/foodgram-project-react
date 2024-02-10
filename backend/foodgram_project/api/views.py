from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
import io
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import streaminghttpresponse
from rest_framework.response import response
from rest_framework import status
from io import bytesio

import tempfile

from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph


from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import AuthorOnly
from api.serializers import (ChangePasswordSerializer,
                             FavoriteSerializer,
                             FollowSerializer,
                             IngredientSerializer,
                             RecipeCreateSerializer,
                             RecipeReadOnlySerializer,
                             ShoppingListSerializer,
                             TagSerializer,
                             UsersInSubscriptionSerializer,
                             UserSerializer,
                             UserSignupSerializer,
                             )
from recipes.models import (Favorite,
                            Follow,
                            Ingredient,
                            IngredientRecipe,
                            Recipe,
                            ShoppingList,
                            Tag,
                            )
from users.models import User


class ListCreateDestroyViewSet(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet,
                               ):
    pagination_class = CustomPagination


class IngredientViewSet(ReadOnlyModelViewSet):
    """Ингредиенты."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    """Теги."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ListCreateDestroyViewSet):
    """Рецепт."""
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly,]

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        if self.action in ['favorite']:
            return FavoriteSerializer
        if self.action in ['shopping_cart']:
            return ShoppingListSerializer
        if self.action in ['list', 'retrieve']:
            return RecipeReadOnlySerializer

    def partial_update(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        tags = request.data.get('tags', None)
        ingredients = request.data.get('ingredients', None)
        if recipe.author == user:
            if not tags or not ingredients:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(
                recipe, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if recipe.author == user:
            if not Recipe.objects.filter(author=user, id=pk).exists():
                return Response(status=status.HTTP_404_NOT_FOUND)
            Recipe.objects.filter(author=user, id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_name='favorite',
    )
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
                recipe_in_fav = Favorite.objects.filter(
                    user=user, recipe=recipe
                )
                if recipe_in_fav.exists():
                    return Response(
                        {'error': 'Вы уже добавили этот рецепт в избранное'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                Favorite.objects.create(user=user, recipe=recipe)
                serializer = self.get_serializer(
                    recipe, context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            except Recipe.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            recipe_in_fav = Favorite.objects.filter(user=user, recipe=recipe)
            if recipe_in_fav.exists():
                recipe_in_fav.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            if not recipe_in_fav.exists():
                return Response(
                    {'error': 'Вы не добавляли этот рецепт в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
                recipe_in_cart = ShoppingList.objects.filter(
                    user=user, recipe=recipe
                )
                if recipe_in_cart.exists():
                    return Response(
                        {'error':
                         'Вы уже добавили этот рецепт в список покупок'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                ShoppingList.objects.create(user=user, recipe=recipe)
                serializer = self.get_serializer(
                    recipe, context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            except Recipe.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            recipe_in_cart = ShoppingList.objects.filter(
                user=user, recipe=recipe
            )
            if recipe_in_cart.exists():
                recipe_in_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            if not recipe_in_cart.exists():
                return Response(
                    {'error': 'Вы не добавляли этот рецепт в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=False,
        methods=['get'],
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = request.user
        if user.is_anonymous:
            return Response(
                {'detail': 'Вы не авторизаваны'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        ingredients_in_shoplist = IngredientRecipe.objects.filter(
            recipe__shopping__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by()
        shopping_list_str = 'Список покупок:\n'
        for shopplist in ingredients_in_shoplist:
            shopping_list_str += (
                f'- {shopplist["ingredient__name"]} - '
                f'{shopplist["amount"]} '
                f'{shopplist["ingredient__measurement_unit"]}\n'
            )

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(60, 800, shopping_list_str)
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename="shoppinglist.pdf"
        )


class CustomUserViewSet(UserViewSet,
                        ListCreateDestroyViewSet,
                        ):
    """Пользователи."""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly,]

    def get_serializer_class(self):
        if self.action in ['create']:
            return UserSignupSerializer
        if self.action in ['set_password']:
            return ChangePasswordSerializer
        if self.action in ['me', 'list', 'retrieve']:
            return UserSerializer
        if self.action in ['subscribe']:
            return FollowSerializer
        if self.action in ['subscriptions']:
            return UsersInSubscriptionSerializer

    @action(
        detail=False,
        methods=['post'],
        url_name='set_password',
    )
    def set_password(self, request):
        user = request.user
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        if not request.user.check_password(
            request.data.get('current_password')
        ):
            return Response(
                {'current_password': 'Неверный пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid(raise_exception=True):
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AuthorOnly,],
        url_name='me',
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_name='subscribe',
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        author_in_subc = Follow.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if user != author:
                if author_in_subc.exists():
                    return Response(
                        {'error': 'Вы уже подписаны на этого пользователя'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                Follow.objects.create(user=user, author=author)
                serializer = self.get_serializer(
                    author, context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if author_in_subc.exists():
                author_in_subc.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            if not author_in_subc.exists():
                return Response(
                    {'error': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=False,
        methods=['get'],
        url_name='subscriptions',
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)
