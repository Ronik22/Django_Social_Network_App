from django.contrib.auth.decorators import login_required
from django.urls import URLResolver, path

from . import views
from .views import (
    AllLikeView,
    AllSaveView,
    LikeCommentView,
    LikeView,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostListView,
    PostUpdateView,
    SaveView,
    UserPostListView,
    posts_of_following_profiles,
)

urlpatterns: list[URLResolver] = [
    path("", views.first, name="firsthome"),
    path("home/", login_required(PostListView.as_view()), name="blog-home"),
    path("feed/", posts_of_following_profiles, name="posts-follow-view"),
    path(
        "post/user/<str:username>/", login_required(UserPostListView.as_view()), name="user-posts"
    ),
    path("post/<int:pk>/", PostDetailView, name="post-detail"),
    path("post/<int:pk>/update/", login_required(PostUpdateView.as_view()), name="post-update"),
    path("post/<int:pk>/delete/", login_required(PostDeleteView.as_view()), name="post-delete"),
    path("post/new/", login_required(PostCreateView.as_view()), name="post-create"),
    path("post/like/", LikeView, name="post-like"),
    path("liked-posts/", AllLikeView, name="all-like"),
    path("post/save/", SaveView, name="post-save"),
    path("saved-posts/", AllSaveView, name="all-save"),
    path("post/comment/like/", LikeCommentView, name="comment-like"),
    path("about/", views.about, name="blog-about"),
    path("search/", views.search, name="search"),
]
