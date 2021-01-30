from django.urls import path
from . import views
from .views import AllSaveView, PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, SaveView, UserPostListView, LikeView,LikeCommentView, posts_of_following_profiles,  AllLikeView

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('feed/', posts_of_following_profiles, name='posts-follow-view'),
    path('post/user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView, name='post-detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/like/', LikeView, name='post-like'),
    path('liked-posts/', AllLikeView, name='all-like'),
    path('post/<int:pk>/save/', SaveView, name='post-save'),
    path('saved-posts/', AllSaveView, name='all-save'),
    # path('post/<int:pk>/comment/', add_comment, name='post-comment'),
    path('post/<int:id1>/comment/<int:id2>/like/', LikeCommentView, name='comment-like'),
    path('about/', views.about, name='blog-about'),
    path('search/', views.search, name='search'),
]