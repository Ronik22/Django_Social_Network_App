from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Submit
from django import forms
from PIL import Image

from events.models import Event


class NewEventForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    event_author = forms.FloatField(widget=forms.HiddenInput(), required=False)
    event_name = forms.CharField(label="Event Name", max_length=120)
    event_start = forms.DateTimeField(label="Event Start")
    event_end = forms.DateTimeField(label="Event End")
    host_email = forms.EmailField()
    host_name = forms.CharField(label="Event Host Name", max_length=120)
    event_description = forms.CharField(label="Event Description")
    registration_deadline = forms.DateTimeField(
        label="Registration Deadline",
    )
    event_poster = forms.ImageField(
        label=("Poster for Event"),
        error_messages={"invalid": ("Image files only")},
        widget=forms.FileInput,
        required=False,
    )

    class Meta:
        model = Event
        fields: list[str] = [
            "event_name",
            "event_start",
            "event_end",
            "host_email",
            "host_name",
            "event_description",
            "registration_deadline",
            "event_poster",
        ]
        widgets = {
            "event_start": DateTimePickerInput(),
            "event_end": DateTimePickerInput(),
            "registration_deadline": DateTimePickerInput(),
            "event_poster": forms.FileInput(),
        }

    helper = FormHelper()
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Submit", css_class="btn btn-info"))
    helper.add_input(Button("cancel", "Cancel", css_class="btn btn-danger", href="/"))

    """Saving Cropped Image"""

    def save(self, *args, **kwargs):
        img = super(NewEventForm, self).save(*args, **kwargs)

        x = self.cleaned_data.get("x")
        y = self.cleaned_data.get("y")
        w = self.cleaned_data.get("width")
        h = self.cleaned_data.get("height")

        if x and y and w and h:
            image = Image.open(img.image)
            cropped_image = image.crop((x, y, w + x, h + y))
            resized_image = cropped_image.resize((300, 300), Image.ANTIALIAS)
            resized_image.save(img.image.path)

        return img
