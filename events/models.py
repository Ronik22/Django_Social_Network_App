import uuid

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

from users.models import Profile

# Create your models here.


def get_image_filename(instance, filename) -> str:
    title = instance.event_name
    slug = slugify(title)
    return f"event_posters/{slug}-{filename}"


class Event(models.Model):
    event_id = models.CharField(max_length=100, default=uuid.uuid4)
    event_posted = models.DateTimeField(default=timezone.now)
    event_author = models.ForeignKey(Profile, on_delete=models.CASCADE)  # new
    event_name = models.CharField(max_length=120)
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    host_email = models.EmailField(max_length=100)
    host_name = models.CharField(max_length=100)
    event_description = models.CharField(max_length=10000)
    registration_deadline = models.DateTimeField()
    event_poster = models.ImageField(upload_to=get_image_filename, null=True, blank=True)
    event_participants: models.ManyToManyField = models.ManyToManyField(
        Profile, related_name="event_participants", null=True, blank=True
    )

    @property
    def event_details(self) -> list[str]:
        return [
            f"Event Name: {self.event_name}",
            f"Event Author: {self.event_author}",
            f"Event Posted: {self.event_posted.strftime('%Y-%m-%d %I:%M %p')}",
            f"Event Starts: {self.event_start.strftime('%Y-%m-%d %I:%M %p')}",
            f"Event Ends: {self.event_end.strftime('%Y-%m-%d %I:%M %p')}",
            f"Registration Deadline: {self.registration_deadline.strftime('%Y-%m-%d %I:%M %p')}",
            f"Event Host: {self.host_name}",
            f"Event Description: {self.event_description}",
        ]


class Participant(models.Model):
    pevent_id = models.CharField(max_length=100)
    participant_email = models.EmailField(max_length=100)
    participant_name = models.CharField(max_length=100)
    participant_contactno = models.IntegerField()
    group_registration = models.BooleanField()
    no_of_members = models.IntegerField()
