from rest_framework import serializers
from .models import User, Post, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "text", "author", "post", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    # shows comments as strings using Comment.__str__()
    comments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ["id", "content", "author", "created_at", "comments"]
