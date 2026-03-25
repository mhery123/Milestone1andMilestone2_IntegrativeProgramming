from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.cache import cache
 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
 
from .permissions import IsPostAuthor, IsAdminRole, IsAdminOrPostAuthor, CanViewPost, IsNotGuest
from .models import Post, Comment, Like
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer
 
from posts.factories.post_factory import PostFactory
from posts.singletons.logger_singleton import LoggerSingleton
 
logger = LoggerSingleton().get_logger()
 
User = get_user_model()
 
 
# ─────────────────────────────────────────
# Pagination class
# ─────────────────────────────────────────
 
class FeedPagination(PageNumberPagination):
    """
    DRF pagination for the feed.
    Default: 5 posts per page.
    Client can override with ?page_size=N (max 20).
    Usage: GET /posts/feed/?page=2
           GET /posts/feed/?page=2&page_size=10
    """
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 20
    page_query_param = "page"
 
 
# ─────────────────────────────────────────
# Cache helpers
# ─────────────────────────────────────────
 
FEED_CACHE_TIMEOUT = 60 * 5  # 5 minutes
 
def get_feed_cache_key(user_id, page, page_size):
    """Unique cache key per user + page + page_size."""
    return f"feed_user_{user_id}_page_{page}_size_{page_size}"
 
def invalidate_feed_cache(user_id):
    """
    Call this whenever a post is created, updated, or deleted
    so the feed cache does not serve stale data.
    Clears pages 1-10 for the user (covers most cases).
    """
    for page in range(1, 11):
        for size in [5, 10, 20]:
            cache.delete(get_feed_cache_key(user_id, page, size))
 
 
# ─────────────────────────────────────────
# Views
# ─────────────────────────────────────────
 
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
 
            # Invalidate feed cache so new post appears immediately
            invalidate_feed_cache(request.user.id)
 
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
    GET    - Enforce privacy: only author can see private posts.
    PUT    - Only the post author or admin can edit.
    DELETE - Only admin users can delete posts.
    """
 
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), CanViewPost()]
        elif self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdminRole()]
        else:
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
            invalidate_feed_cache(request.user.id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        invalidate_feed_cache(request.user.id)
        logger.info(f"Post {pk} deleted by admin user={request.user.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)
 
 
class PostLike(APIView):
    permission_classes = [IsAuthenticated, IsNotGuest]
 
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
 
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
 
        if post.privacy == "private" and post.author != request.user:
            return Response(
                {"error": "This post is private."},
                status=status.HTTP_403_FORBIDDEN
            )
 
        comments = Comment.objects.filter(post=post).select_related("author")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
 
 
class FeedListView(APIView):
    """
    GET /posts/feed/
    - Paginated: ?page=1&page_size=5 (default)
    - Cached: results cached per user+page+page_size for 5 minutes
    - Privacy: shows public posts + user's own private posts
    - Optimized: uses select_related and prefetch_related to reduce DB queries
    """
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        paginator = FeedPagination()
 
        # Determine page and page_size for cache key
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get(
            paginator.page_size_query_param, paginator.page_size
        )
        cache_key = get_feed_cache_key(request.user.id, page, page_size)
 
        # Try to return cached response
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Feed cache HIT user={request.user.id} page={page}")
            return Response(cached_data)
 
        logger.info(f"Feed cache MISS user={request.user.id} page={page}")
 
        # Query: public posts + user's own private posts
        # select_related preloads author in same DB query (avoids N+1 queries)
        # prefetch_related preloads comments and likes in bulk queries
        posts = (
            Post.objects.filter(privacy="public") |
            Post.objects.filter(author=request.user)
        ).distinct().select_related("author").prefetch_related(
            "comments", "likes"
        ).order_by("-created_at")
 
        # Paginate using DRF PageNumberPagination
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
 
        # Cache the paginated response data for 5 minutes
        response_data = paginated_response.data
        cache.set(cache_key, response_data, FEED_CACHE_TIMEOUT)
 
        return Response(response_data)