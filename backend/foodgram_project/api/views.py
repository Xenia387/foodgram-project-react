from django.db.models import Sum
# from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework import (
    # filters,
    mixins, permissions, status, viewsets
)
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, action
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

import reportlab
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas


from api.pagination import (
    # RecipePagination,
    CustomPagination,
)
from api.permissions import (
    IsAdminOrSuperUser,
    AuthorOrReadOnly,
    IsAuthorOrAdminOrReadOnly,
    IsAdminOrOther,
    ReadOnly,
)
from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag,
    Favorite,
    Follow,
    ShoppingList,
)
from users.models import User
from api.serializers import (
    IngredientSerializer,
    TagSerializer,
    UserSerializer,
    UserSignupSerializer,
    RecipeReadOnlySerializer,
    UsersInSubscriptionSerializer,
    RecipeCreateSerializer,
    FavoriteSerializer,
    FollowSerializer,
    ChangePasswordSerializer,
    ShoppingListSerializer,

    RecipeInFavoriteAndShopList,
    IngredientsAmountInShoppingCartSerializer,
    UsersInSubscriptionSerializer,
)

from api.permissions import (
    IsAdminOrSuperUser,
    AuthorOrReadOnly,
    IsAuthorOrAdminOrReadOnly,
    IsAdminOrOther,
)
from api.filters import (
    IngredientFilter,
    RecipeFilter,
)


class UpdateDestroyViewSet(
    viewsets.ModelViewSet,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class CreateListViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


class ListCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pass


class IngredientViewSet(ReadOnlyModelViewSet):
    """Ингредиенты."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    http_method_names = ('get',)


class TagViewSet(ReadOnlyModelViewSet):
    """Теги."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ListCreateDestroyViewSet):
    """Рецепт."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'delete']:
            return RecipeCreateSerializer
        if self.action in ['get']:
            return RecipeReadOnlySerializer
        else:
            return RecipeReadOnlySerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated,],
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(user, recipe)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response({'error': 'Рецепт уже добавлен в избранное'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated,],
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def add_shopping_cart(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            return Response({'error': 'Рецепт уже добавлен в список покупок'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = ShoppingListSerializer
            serializer.save(user=request.user)
            return Response(**serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated,],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response({'detail': 'Учетные данные не были предоставлены'}, status=status.HTTP_401_UNAUTHORIZED)
        ingredients_in_shoplist = IngredientRecipe.objects.filter(
            recipe__shopping__user=user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
                ).annotate(amount=Sum('amount')).order_by()
        shopping_list_str = 'Список покупок shopp:'
        for shopplist in ingredients_in_shoplist:
            shopping_list_str += f'- {shopplist["ingredient__name"]} - {shopplist["amount"]} {shopplist["ingredient__measurement_unit"]}'

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(60, 800, shopping_list_str)
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="shoppinglist.pdf")


class CustomUserViewSet(
    UserViewSet,
    ListCreateDestroyViewSet
):
    """Пользователи."""
    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['set_password']:
            return ChangePasswordSerializer
        if self.action in ['list', 'me', 'retrieve']:
            return UserSerializer
        if self.action in ['create']:
            return UserSignupSerializer
        else:
            return UserSerializer

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password',
        url_name='set_password',
    )
    def set_password(self, request, pk=None):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated,],
        url_path='me',
        url_name='me',
    )
    def me(self, request):
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated,],
        url_name='subscribe',
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, id=pk)

        if Follow.objects.filter(user=user, author=author).exists():
            return Response({'error': 'Вы уже подписаны на этого пользователя'}, status=status.HTTP_STATUS_400_BAD_REQUEST)
        serializer = FollowSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)