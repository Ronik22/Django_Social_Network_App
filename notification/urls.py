from django.urls import path
from django.urls.resolvers import URLPattern
from notification.views import ShowNotifications

urlpatterns = [
    path('', ShowNotifications, name='show-notifications'),
]