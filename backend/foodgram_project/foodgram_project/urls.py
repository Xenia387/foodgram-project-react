from django.contrib import admin
from django.urls import include, path

from rest_framework.authtoken import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # path('api/v1/auth/token/login', views.obtain_auth_token),
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.jwt')),
]

# from cats.views import AchievementViewSet, CatViewSet
# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib import admin
# from django.urls import include, path
# from rest_framework import routers

# router = routers.DefaultRouter()
# router.register(r'cats', CatViewSet)
# router.register(r'achievements', AchievementViewSet)

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include(router.urls)),
#     path('api/', include('djoser.urls')),  # Работа с пользователями
#     path('api/', include('djoser.urls.authtoken')),  # Работа с токенами
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)