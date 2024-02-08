from rest_framework import permissions


class AuthorOnly(permissions.BasePermission):
    """Доступ к странице Текущего пользователя."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
