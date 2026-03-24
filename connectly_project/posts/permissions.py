from rest_framework.permissions import BasePermission, SAFE_METHODS
 
 
class IsPostAuthor(BasePermission):
    """Allow access only to the post's author."""
 
    message = "You must be the author of this post."
 
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
 
 
class IsAdminRole(BasePermission):
    """Allow access only to users with the 'admin' role."""
 
    message = "Only admin users can perform this action."
 
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )
 
 
class IsNotGuest(BasePermission):
    """Deny write access to guests; allow read-only."""
 
    message = "Guest users cannot perform this action."
 
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role != "guest"
 
 
class CanViewPost(BasePermission):
    """
    Object-level permission to enforce post privacy:
    - Public posts: any authenticated user can view.
    - Private posts: only the author can view.
    """
 
    message = "This post is private."
 
    def has_object_permission(self, request, view, obj):
        if obj.privacy == "public":
            return True
        # private post — only the author can see it
        return obj.author == request.user
 
 
class IsAdminOrPostAuthor(BasePermission):
    """
    Allow delete/edit if the user is either:
    - an admin role user, OR
    - the post's author
    """
 
    message = "Only the post author or an admin can perform this action."
 
    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True
        return obj.author == request.user