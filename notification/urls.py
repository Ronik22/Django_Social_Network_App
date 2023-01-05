from django.urls import path

from notification.views import ShowNotifications, notification_status

app_name = "notification"

urlpatterns = [
    path("", ShowNotifications, name="show-notifications"),
    path("notification/status/", notification_status, name="notification-status"),
]
