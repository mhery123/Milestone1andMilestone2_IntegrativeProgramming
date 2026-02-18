from django.urls import path
from .views import UserListCreate, PostListCreate, CommentListCreate, PostDetail
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("users/", UserListCreate.as_view(), name="user-list-create"),
    path("posts/", PostListCreate.as_view(), name="post-list-create"),
    path("posts/<int:pk>/", PostDetail.as_view(), name="post-detail"),
    path("comments/", CommentListCreate.as_view(), name="comment-list-create"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

]
