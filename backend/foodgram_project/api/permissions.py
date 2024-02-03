from rest_framework import permissions


class IsAdminOrSuperUser(permissions.BasePermission):
    """Разрешение для админа или суперюзера."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class AuthorOrReadOnly(permissions.BasePermission):
    """."""
    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
            )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Изменять записи может только их автор."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            # or request.user.is_admin
            # or request.user.is_moderator
        )


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Изменять записи может только их автор."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )


class IsAdminOrOther(permissions.BasePermission):
    """Разрешение для админа или суперюзера."""
    def has_permission(self, request, view):
        """Создавать, изменять и удалять категории, жанры и произведения
        может только админ."""
        return (
            (
                request.user.is_authenticated
                and request.user.is_admin
            )
            or request.method in permissions.SAFE_METHODS
        )


class ReadOnly(permissions.BasePermission):
    """."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
