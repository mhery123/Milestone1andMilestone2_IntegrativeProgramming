from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
 
from .permissions import IsPostAuthor, IsAdminRole, IsAdminOrPostAuthor, CanViewPost, IsNotGuest
from .models import Post, Comment, Like
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer
 
from posts.factories.post_factory import PostFactory
from posts.singletons.logger_singleton import LoggerSingleton
 
logger = LoggerSingleton().get_logger()
 
User = get_user_model()
 
 
class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
 
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class UserRoleUpdate(APIView):
    """Admin-only endpoint to change a user's role."""
    permission_classes = [IsAuthenticated, IsAdminRole]
 
    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        new_role = request.data.get("role")
 
        valid_roles = [r[0] for r in User.Role.choices]
        if new_role not in valid_roles:
            return Response(
                {"error": f"Invalid role. Choose from: {valid_roles}"},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        user.role = new_role
        user.save()
        return Response(
            {"message": f"Role updated to '{new_role}' for user '{user.username}'"},
            status=status.HTTP_200_OK
        )
 
 
class PostListCreate(APIView):
    permission_classes = [IsAuthenticated, IsNotGuest]
 
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
 
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                f"Post validation failed user={request.user.id} errors={serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            post = PostFactory.create_post(
                author=request.user,
                content=serializer.validated_data.get("content", ""),
                privacy=serializer.validated_data.get("privacy", "public")
            )
            logger.info(f"Post created id={post.id} user={request.user.id}")
            return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
 
        except ValueError as e:
            logger.warning(f"Post creation failed user={request.user.id} error={str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
 
class CommentListCreate(APIView):
    permission_classes = [IsAuthenticated, IsNotGuest]
 
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
 
    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class PostDetail(APIView):
    """
    GET  - Enforce privacy: only author can see private posts.
    PUT  - Only the post author or admin can edit.
    DELETE - Only admin users can delete posts.
    """
 
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), CanViewPost()]
        elif self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdminRole()]
        else:  # PUT / PATCH
            return [IsAuthenticated(), IsAdminOrPostAuthor()]
 
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
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        # Admin check is at view level; no object-level check needed
        post.delete()
        logger.info(f"Post {pk} deleted by admin user={request.user.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)
 
 
class PostLike(APIView):
    permission_classes = [IsAuthenticated, IsNotGuest]
 
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
 
        # Enforce privacy — guests/non-authors can't like private posts
        if post.privacy == "private" and post.author != request.user:
            return Response(
                {"error": "You cannot like a private post."},
                status=status.HTTP_403_FORBIDDEN
            )
 
        like, created = Like.objects.get_or_create(user=request.user, post=post)
 
        if created:
            return Response(
                {"message": "Post liked successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": "You already liked this post"},
            status=status.HTTP_200_OK
        )
 
 
class PostCommentCreate(APIView):
    permission_classes = [IsAuthenticated, IsNotGuest]
 
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
 
        # Enforce privacy — can't comment on private posts you don't own
        if post.privacy == "private" and post.author != request.user:
            return Response(
                {"error": "You cannot comment on a private post."},
                status=status.HTTP_403_FORBIDDEN
            )
 
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class PostCommentsList(APIView):
    permission_classes = [IsAuthenticated]
 
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
 
        # Enforce privacy
        if post.privacy == "private" and post.author != request.user:
            return Response(
                {"error": "This post is private."},
                status=status.HTTP_403_FORBIDDEN
            )
 
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
 
 
class FeedListView(APIView):
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        page = request.query_params.get("page", 1)
        page_size = 5
 
        try:
            page = int(page)
            if page < 1:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "Invalid page number"},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        # Show public posts to everyone; show the user's own private posts too
        posts = Post.objects.filter(
            privacy="public"
        ) | Post.objects.filter(
            author=request.user
        )
        posts = posts.distinct().order_by("-created_at")
 
        start = (page - 1) * page_size
        end = start + page_size
        paginated_posts = posts[start:end]
 
        serializer = PostSerializer(paginated_posts, many=True)
        return Response({
            "page": page,
            "page_size": page_size,
            "results": serializer.data
        })