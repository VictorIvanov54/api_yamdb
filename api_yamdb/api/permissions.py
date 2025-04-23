from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Права доступа - только администратор может просматривать
    и редактировать данные.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """Права доступа администратору, или только чтение."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin)


class IsAuthorOrModeratorOrAdmin(BasePermission):
    """
    Права доступа автору, модератору и администратору.
    Другим пользователям - только чтение.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated and (
                obj.author == request.user or request.user.is_moderator
                or request.user.is_admin
            )
        )
