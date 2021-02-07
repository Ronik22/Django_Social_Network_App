from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='msg_from_user')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='msg_to_user')
    text = models.CharField(max_length=300)
    date = models.DateTimeField(auto_now_add=True)
    has_seen = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s - %s' %(self.id, self.sender, self.receiver)