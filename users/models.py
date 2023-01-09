from django.contrib.auth.models import User
from django.db import models

RELATIONSHIP_STATUS_CHOICES = (("send", "send"), ("accepted", "accepted"))

""" Model for User Profile """


class Profile(models.Model):
    user: models.OneToOneField = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online: models.BooleanField = models.BooleanField(default=False)
    following: models.ManyToManyField = models.ManyToManyField(
        User, related_name="following", blank=True
    )
    friends: models.ManyToManyField = models.ManyToManyField(
        User, related_name="my_friends", blank=True
    )
    bio: models.CharField = models.CharField(default="", null=True, max_length=350)
    date_of_birth: models.DateField = models.DateField(null=True)
    updated: models.DateTimeField = models.DateTimeField(auto_now=True)
    created: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    image: models.ImageField = models.ImageField(
        default="default.jpg", upload_to="profile_pics", blank=True, null=True
    )
    verified: models.BooleanField = models.BooleanField(default=False)
    relationship_status_override: models.BooleanField = models.BooleanField(default=False)
    relationship_status: models.CharField = models.CharField(
        choices=[
            ("single_male", "Single Male"),
            ("single_female", "Single Female"),
            ("couple", "Couple"),
        ],
        null=True,
        max_length=17,
    )

    sls_username: models.CharField = models.CharField(blank=True, null=True, max_length=150)
    how_did_you_hear_about_us: models.CharField = models.CharField(null=True, max_length=350)
    facebook_link: models.CharField = models.CharField(blank=True, null=True, max_length=200)
    instagram_link: models.CharField = models.CharField(blank=True, null=True, max_length=200)
    twitter_link: models.CharField = models.CharField(blank=True, null=True, max_length=200)

    def profile_posts(self):
        return self.user.post_set.all()

    def get_friends(self):
        return self.friends.all()

    def get_friends_no(self) -> int:
        return self.friends.all().count()

    def get_verified_status(self) -> bool:
        return self.verified

    def get_user_relationship_status(self) -> str:
        return self.relationship_status

    def __str__(self) -> str:
        return f"{self.user.username}"


class BlockList(models.Model):
    email = models.EmailField(unique=True, null=True)  # don't want conflicting results


class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="friend_sender")
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="friend_receiver")
    status = models.CharField(max_length=8, choices=RELATIONSHIP_STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
