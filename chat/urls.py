from django.urls import path
from chat.views import ChatView, AllChat

urlpatterns = [
    path('<int:id>/', ChatView, name="chat"),
    path('all/', AllChat, name="all-chat"),
]