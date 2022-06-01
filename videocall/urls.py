from django.urls import path
from . import views

urlpatterns = [
    path('', views.lobby, name='vc-lobby'),
    path('room/', views.room, name='vc-room'),
    path('get_token/', views.getToken),

    path('create_member/', views.createMember),
    path('get_member/', views.getMember),
    path('delete_member/', views.deleteMember),
]