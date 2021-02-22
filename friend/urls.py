from django.urls import path
from django.urls.resolvers import URLPattern
from friend.views import cancel_friend_request, decline_friend_request, friend_requests, friends_list_view, remove_friend, send_friend_request, accept_friend_request

app_name = "friend"

urlpatterns = [
    path('list/<user_id>', friends_list_view, name='list'),
    path('friend_request/', send_friend_request, name="friend-request"),
    path('friend_requests/<user_id>/', friend_requests, name='friend-requests'),
    path('friend_request_accept/<friend_request_id>/', accept_friend_request, name='friend-request-accept'),
    path('friend_remove/', remove_friend, name='remove-friend'),
    path('friend_request_decline/<friend_request_id>/', decline_friend_request, name='friend-request-decline'),
    path('friend_request_cancel/', cancel_friend_request, name='friend-request-cancel'),
]