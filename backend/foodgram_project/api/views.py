from django.db.models import Sum
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend # !!!!!!!!!!!
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
    # filter_backends = [filters.SearchFilter,] # от наставника
    # filter_backends = [DjangoFilterBackend] # от наставника
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
    # filter_backends = [DjangoFilterBackend] # от наставника
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

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated,],
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        user = self.request.user
        recipe = Recipe.objects.get(id=pk)
        # if Favorite.objects.filter(user=user, recipe=recipe).exists():
        #     return Response({'error': str('Вы уже добавили этот рецепт в избранное')},
        #                     status=status.HTTP_400_BAD_REQUEST)
        # if user.is_anonymous():
        #     return Response({'error': str('Вы не авторизованы')},
        #                     status=status.HTTP_401_UNAUTHORIZED)
        Favorite.objects.creat(user=user, recipe=recipe)
        serializer = RecipeInFavoriteAndShopList(recipe)
        return Favorite.objects.filter(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['delete'],
        permission_classes=[IsAuthenticated,],
        url_path='favorite',
        url_name='favorite',
    )
    def unfavorite(self, request, pk):
        recipe = Recipe.objects.get(id=pk)
        if not Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            return Response({'error': 'Вы не добавляли этот рецепт в избранное'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user_anonymous():
            return Response({'error': str('Вы не авторизованы')},
                            status=status.HTTP_401_UNAUTHORIZED)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(
    #     detail=False,
    #     permission_classes=[IsAuthenticated,],
    #     url_path='download_shopping_cart',
    #     url_name='download_shopping_cart',
    # )
    # def dowload_shopping_list(self, request):
        # pass


# class UserViewSet(UserViewSet):
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


    # @action(
    #     detail=False,
    #     methods=['patch'],
    #     permission_classes=[IsAuthenticated,],
    #     url_path='set_password',
    #     url_name='set_password',
    # )
    # def set_password(self, request):
    #     user = self.request.user
    #     serializer = self.get_serializer(data=request.data)
    #     # serialized = UserSerializer(data=request.DATA)
    #     if serialized.is_valid():
    #         user.set_password(serialized.data['password'])
    #         user.save()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     if user.is_anonymous:
    #         return Response(status=status.HTTP_401_UNAUTHORIZED)
    #     else:
    #         return Response({'field_name': str('Все поля обязательны для заполнения')}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated,],
        url_path='subcribe',
        url_name='subcribe',
    )
    def subcribe(self, request, pk):
        user = self.request.user
        author = User.objects.get(id=pk)
        if Follow.objects.create(user=user, author=author).exists():
            return Response({'error': str('Непредвиденная ошибка')},
                            status=status.HTTP_400_BAD_REQUEST)
        if user.is_anonymous():
            return Response({'error': str('Вы не авторизованы')},
                            status=status.HTTP_401_UNAUTHORIZED)
        Follow.objects.creat(user=user, rauthor=author)
        serializer = RecipeInFavoriteAndShopList(author)
        return Favorite.objects.filter(serializer.data, status=status.HTTP_201_CREATED)

    # @action(
    #     detail=False,   # ?
    #     # methods=['get'],
    #     permission_classes=[IsAuthenticated,],
    #     url_path='subcriptions',
    #     url_name='subcriptions',
    # )
    # def subcriptions(self, request):
    #     user = request.user
    #     if user.is_anonymous():
    #         return Response({'error': str('Вы не авторизованы')},
    #                         status=status.HTTP_401_UNAUTHORIZED)
    #     else:
    #         serialier = UsersInSubscriptionSerializer
