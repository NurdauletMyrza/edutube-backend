from rest_framework.permissions import BasePermission


class IsNotAdmin(BasePermission):
    """
    Custom permission to allow access only to non-admin users.
    """

    def has_permission(self, request, view):
        # Заблокировать доступ, если текущий пользователь — админ
        return request.user.role != 'admin'
