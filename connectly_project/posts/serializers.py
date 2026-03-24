from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Post, Comment, Like
 
User = get_user_model()
 
 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role"]
        read_only_fields = ["role"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
 
 
class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
 
    class Meta:
        model = Comment
        fields = ["id", "text", "author_username", "post", "created_at"]
        read_only_fields = ["post", "author_username", "created_at"]
 
 
class PostSerializer(serializers.ModelSerializer):
    comments = serializers.StringRelatedField(many=True, read_only=True)
 
    class Meta:
        model = Post
        fields = ["id", "content", "author", "created_at", "comments", "privacy"]
        read_only_fields = ["author", "created_at", "comments"]
 
 
class LikeSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
 
    class Meta:
        model = Like
        fields = ["id", "user_username", "post", "created_at"]
        read_only_fields = ["post", "user_username", "created_at"]
 