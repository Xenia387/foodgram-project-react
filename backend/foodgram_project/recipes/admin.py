from django.contrib import admin

from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag,
    TagRecipe,
    ShoppingList,
    Favorite,
    Follow,
)


class IngredientRecipeInline(admin.TabularInline):
    model = Recipe.ingredients.through


class TagRecipeInline(admin.TabularInline):
    model = Recipe.tags.through


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
        # 'amount',
    )
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientRecipeInline, TagRecipeInline,]
    list_display = (
        'name',
        'author',
        # 'is_favorited',
        # 'favorite_count',
        # 'tag',
        # 'is_in_shopping_cart',
        # 'cart_count',
    )
    list_filter = (
        'author',
        'name',
        # 'tag',
    )
    # search_fields = ('name', 'author', 'tags')


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )
    list_filter = ('name',)


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )


admin.site.register(ShoppingList)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(TagRecipe)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
