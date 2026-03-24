from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
 
 
class User(AbstractUser):
    """Custom user model with role support."""
 
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        USER = "user", "User"
        GUEST = "guest", "Guest"
 
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
 
    def __str__(self):
        return f"{self.username} ({self.role})"
 
    def is_admin(self):
        return self.role == self.Role.ADMIN
 
    def is_guest(self):
        return self.role == self.Role.GUEST
 
 
class Post(models.Model):
 
    class Privacy(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
 
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="posts",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    privacy = models.CharField(
        max_length=10,
        choices=Privacy.choices,
        default=Privacy.PUBLIC,
    )
 
    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at} [{self.privacy}]"
 
 
class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"
 
 
class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="likes",
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        related_name="likes",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        unique_together = ("user", "post")
 
    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"