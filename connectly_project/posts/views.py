from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .permissions import IsPostAuthor
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer

from posts.factories.post_factory import PostFactory
from posts.singletons.logger_singleton import LoggerSingleton

logger = LoggerSingleton().get_logger()


User = get_user_model()


class UserListCreate(APIView):
    # optional: you can add permission_classes if you want
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # creates a Django auth user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        # validate input using serializer first
        serializer = PostSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                f"Post validation failed user={request.user.id} errors={serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = PostFactory.create_post(
                author=request.user,
                content=serializer.validated_data.get("content", "")
            )
            logger.info(f"Post created id={post.id} user={request.user.id}")

            return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            logger.warning(f"Post creation failed user={request.user.id} error={str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class CommentListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # ✅ same fix for comments
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # author stays same because it's read_only in serializer
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
