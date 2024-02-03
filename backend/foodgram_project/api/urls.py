from rest_framework.routers import DefaultRouter

from django.contrib import admin
from django.urls import include, path, re_path

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    CustomUserViewSet,
)

router = DefaultRouter()

router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')  


urlpatterns = [
    path('', include(router.urls)),
    path('v1/', include(router.urls)),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
