from django.db.models import Sum
from django.contrib.auth.tokens import default_token_generator
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

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet




from api.pagination import (
    RecipePagination,
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
    UserAfterRegistSerializer,
    UserSerializer,
    # UserRecieveTokenSerializer,
    UserSignupSerializer,
    RecipeReadOnlySerializer,
    UsersInSubscriptionSerializer,
    RecipeCreateSerializer,
    IngredientRecipeSerializer,
    FavoriteSerializer,
    FollowSerializer,
    ChangePasswordSerializer,

    RecipeInFavoriteAndShopList,
    IngredientsAmountInShoppingCart,
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
    # filter_backends = [filters.SearchFilter,]
    # filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    http_method_names = ('get',)


class TagViewSet(ReadOnlyModelViewSet):
    """Теги."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ListCreateDestroyViewSet):
    """Рецепт."""
    queryset = Recipe.objects.all()
    pagination_class = RecipePagination
    # filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'delete']:
            return RecipeCreateSerializer
        if self.action in ['get']:
            return RecipeReadOnlySerializer
        else:
            return RecipeReadOnlySerializer

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)


class UserViewSet(UserViewSet, ListCreateDestroyViewSet):
    """Пользователи."""
    queryset = User.objects.all()
    pagination_class = CustomPagination
    http_method_names = ['post', 'delete', 'get']

    def get_serializer_class(self):
        if self.action in ['list', 'me', 'retrieve']:
            return UserSerializer
        if self.action in ['subcribe']:
            return UserSerializer
        # if self.action in ['set_password']:
        #     return ChangePasswordSerializer
        else:
            # return UserSerializer
            return UserAfterRegistSerializer

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
        detail=False,
        permission_classes=[IsAuthenticated,],
        url_path='subscribe',
        url_name='subscribe',
    )
    def subscribe(self, request, pk):
        user = request.user
        author = User.objects.get(id=pk)
        if Follow.objects.filter(user=user, author=author).exists():
            return('error': 'Непредвиденная ошибка', status=status.HT)
