import logging

from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from protected_media.models import ProtectedImageField
from thumbnails.fields import ImageField


def get_image_filename(instance, filename) -> str:
    try:
        title = instance.title
    except Exception:
        title = instance.post.title
    slug = slugify(title)
    logging.debug(f"Uploading file {slug}-{filename}")
    return f"post_images/{slug}-{filename}"


class ImageModelField(ImageField, ProtectedImageField):
    pass


""" Post model """


class Post(models.Model):
    title: models.CharField = models.CharField(max_length=150)
    content: RichTextField = RichTextField(blank=True, null=True)
    date_posted: models.DateTimeField = models.DateTimeField(default=timezone.now)
    date_updated: models.DateTimeField = models.DateTimeField(auto_now=True)
    author: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    image: models.ImageField = models.ImageField(
        upload_to=get_image_filename, null=True, blank=True
    )
    likes: models.ManyToManyField = models.ManyToManyField(
        User, related_name="blogpost", blank=True
    )
    saves: models.ManyToManyField = models.ManyToManyField(
        User, related_name="blogsave", blank=True
    )

    def total_likes(self) -> int:
        return self.likes.count()

    def total_saves(self) -> int:
        return self.saves.count()

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("post-detail", kwargs={"pk": self.pk})


class Image(models.Model):
    post: models.ForeignKey = models.ForeignKey(
        Post, related_name="images", on_delete=models.CASCADE
    )
    image: ImageModelField = ImageModelField(
        upload_to=get_image_filename,
        null=True,
        blank=True,
        pregenerated_sizes=["small", "large"],
    )

    def __str__(self) -> str:
        return self.post.title


""" Comment model """


class Comment(models.Model):
    post: models.ForeignKey = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE
    )
    name: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    body: models.TextField = models.TextField(max_length=200)
    date_added: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    likes: models.ManyToManyField = models.ManyToManyField(
        User, related_name="blogcomment", blank=True
    )
    reply: models.ForeignKey = models.ForeignKey(
        "self", null=True, related_name="replies", on_delete=models.CASCADE
    )
    is_reply: models.BooleanField = models.BooleanField(default=False)

    def total_clikes(self) -> int:
        return self.likes.count()

    def __str__(self) -> str:
        return "%s - %s - %s" % (self.post.title, self.name, self.id)

    def get_absolute_url(self) -> str:
        return reverse("post-detail", kwargs={"pk": self.pk})
