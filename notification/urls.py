from django.urls import path
from notification.views import ShowNotifications

urlpatterns = [
    path('', ShowNotifications, name='show-notifications'),
]