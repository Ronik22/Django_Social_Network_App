from django.contrib.auth import views as auth_views
from django.urls import URLPattern, path

from . import views

urlpatterns: list[URLPattern] = [
    path("all/", views.ProfileListView.as_view(), name="profile-list-view"),
    path("follow/", views.follow_unfollow_profile, name="follow-unfollow-view"),
    path("<int:pk>/", views.ProfileDetailView.as_view(), name="profile-detail-view"),
    path("public-profile/<str:username>/", views.public_profile, name="public-profile"),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="main/password/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="main/password/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="main/password/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("password_reset/", views.password_reset_request, name="password_reset"),
]
