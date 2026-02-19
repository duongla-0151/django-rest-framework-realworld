from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthorOrReadOnly(BasePermission):
    """
    Custom permission: Only the author can update or delete. Read-only for others.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsCommentAuthor(BasePermission):
    """
    Custom permission: Only the comment author can delete.
    Anonymous and non-author users cannot delete comments.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # Only the comment author can delete
        return obj.author == request.user
