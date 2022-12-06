from django.urls import URLPattern, path

from . import views

urlpatterns: list[URLPattern] = [
    path("all/", views.ProfileListView.as_view(), name="profile-list-view"),
    path("follow/", views.follow_unfollow_profile, name="follow-unfollow-view"),
    path("<int:pk>/", views.ProfileDetailView.as_view(), name="profile-detail-view"),
    path("public-profile/<str:username>/", views.public_profile, name="public-profile"),
]
