from rest_framework.routers import DefaultRouter

from django.contrib import admin
from django.urls import include, path, re_path

from api.views import (
    IngredientViewSet,
    # RecipeDetailViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
    UserViewSet,
    # UserReceiveTokenViewSet,
    # UserReadOnlyViewSet,
)

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
    path('v1/', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
