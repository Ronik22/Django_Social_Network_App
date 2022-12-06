from django import forms
from django.forms import widgets  # noqa: F401

from .models import Comment, Post  # noqa: F401


class CommentForm(forms.ModelForm):
    body: forms.CharField = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control custom-txt", "cols": "40", "rows": "3"}
        ),
        label="",
    )

    class Meta:
        model = Comment
        fields: list[str] = [
            "body",
        ]
