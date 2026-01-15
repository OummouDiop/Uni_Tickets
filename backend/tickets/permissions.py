from rest_framework.permissions import BasePermission

class IsStudent(BasePermission):
    """Permission pour vérifier si l'utilisateur est un étudiant"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'STUDENT'

class IsAdmin(BasePermission):
    """Permission pour vérifier si l'utilisateur est un administrateur"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'

class IsAgent(BasePermission):
    """Permission pour vérifier si l'utilisateur est un agent de restauration"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'AGENT'

class IsAdminOrReadOnly(BasePermission):
    """
    Permission pour que seul un admin puisse modifier,
    les autres peuvent lire
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'
