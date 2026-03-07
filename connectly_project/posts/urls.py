from django.urls import path
from .views import (
    UserListCreate,
    PostListCreate,
    CommentListCreate,
    PostDetail,
    PostLike,
    PostCommentCreate,
    PostCommentsList,
    FeedListView
)
from .auth_views import GoogleLogin


urlpatterns = [
    path("users/", UserListCreate.as_view(), name="user-list-create"),
    path("posts/", PostListCreate.as_view(), name="post-list-create"),
    path("posts/<int:pk>/", PostDetail.as_view(), name="post-detail"),
    path("comments/", CommentListCreate.as_view(), name="comment-list-create"),
    path("posts/<int:pk>/like/", PostLike.as_view(), name="post-like"),
    path("posts/<int:pk>/comment/", PostCommentCreate.as_view(), name="post-comment"),
    path("posts/<int:pk>/comments/", PostCommentsList.as_view(), name="post-comments"),    
    path("auth/google/login/", GoogleLogin.as_view(), name="google-login"),
    path("feed/", FeedListView.as_view(), name="news-feed"),
]
