from django.contrib import admin

from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        # 'is_subscribed',
    )
    list_filter = (
        'first_name',
        'email',
    )


admin.site.register(CustomUser, CustomUserAdmin)
