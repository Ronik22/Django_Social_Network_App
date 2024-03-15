import logging

from django import forms

from .models import Comment, Images, Post  # noqa: F401


class CreateUpdatePostForm(forms.ModelForm):
    images = forms.ImageField(widget=forms.FileInput(attrs={"multiple": True}), required=False)

    class Meta:
        model = Post
        exclude = ["date_posted", "date_updated", "author", "likes", "saves", "image"]

    def post(self, request, *args, **kwargs):
        logging.debug(f"{dir(request)}")
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        images = request.FILES.getlist("images")
        if form.is_valid():
            for image in images:
                Images.objects.create(post=form.instance.post.pk, image=image)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


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
