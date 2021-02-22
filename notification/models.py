from django.db import models
from django.contrib.auth.models import User

# Create your models here.

""" Notification model """
class Notification(models.Model):
    NOTIFICATION_TYPES = ((1,'Like'),(2,'Follow'),(3,'Comment'),(4,'Reply'),(5,'Like-Comment'),(6,'Like-Reply'))

    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='notify_post', blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notify_from_user')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notify_to_user')
    notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
    text_preview = models.CharField(max_length=120, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s - %s - %s - %s' %(self.id, self.post, self.sender, self.user, self.notification_type)