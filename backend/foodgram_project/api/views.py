from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.http import FileResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from rest_framework import (
    mixins, status, viewsets
)
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet


import reportlab
import io
from reportlab.pdfgen import canvas


from api.filters import (
    IngredientFilter,
    RecipeFilter,
)
from api.pagination import (
    CustomPagination,
)
from api.serializers import (
    ChangePasswordSerializer,
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
from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingList,
    Tag,
)
from users.models import User


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
    permission_classes = [IsAuthenticatedOrReadOnly,]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'destroy']:
            return RecipeCreateSerializer
        else:
            return RecipeReadOnlySerializer

    def destroy(self, request, pk):
        user = self.request.user
        if not Recipe.objects.filter(author=user, id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        Recipe.objects.filter(author=user, id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_fav = Favorite.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if recipe_in_fav.exists():
                return Response(
                    {'error': 'Вы уже добавили этот рецепт в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
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
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_cart = ShoppingList.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if recipe_in_cart.exists():
                return Response(
                    {'error': 'Вы уже добавили этот рецепт в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = ShoppingListSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if recipe_in_cart.exists():
                recipe_in_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            if not recipe_in_cart.exists():
                return Response(
                    {'error': 'Вы не добавляли этот рецепт в список покупоу'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=False,
        methods=['get'],
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
            shopping_list_str += f'- {shopplist["ingredient__name"]} - '
            f'{shopplist["amount"]} '
            f'{shopplist["ingredient__measurement_unit"]}'

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(60, 800, shopping_list_str)
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename="shoppinglist.pdf"
        )


class CustomUserViewSet(
    UserViewSet,
    ListCreateDestroyViewSet
):
    """Пользователи."""
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedOrReadOnly,]

    def get_serializer_class(self):
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
    def set_password(self, request):
        user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if not request.user.check_password(
            request.data.get('current_password')
        ):
            return Response(
                {'current_password': 'Неверный пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            user.set_password(serializer.validated_data.get('new_password'))
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
        methods=['post', 'delete'],
        url_name='subscribe',
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        author_in_subc = Follow.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if user == author:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if author_in_subc.exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if author_in_subc.exists():
                author_in_subc.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            if not author_in_subc.exists():
                return Response(
                    {'error': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
