from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_enroll, name='room-enroll'),
    path('chat/<int:friend_id>', views.room_choice, name='room-choice'),
    path('room/<int:room_name>-<int:friend_id>', views.room, name='room'),
]