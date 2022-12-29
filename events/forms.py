from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django import forms

from events.models import Event


class NewEventForm(forms.ModelForm):
    class Meta:
        model = Event
        event_author = forms.CharField(max_length=120)
        event_name = forms.CharField(label="Event Name", max_length=120)
        event_start = forms.DateTimeField(label="Event Start")
        event_end = forms.DateTimeField(label="Event End")
        host_email = forms.EmailField()
        host_name = forms.CharField(label="Event Host Name", max_length=120)
        event_description = forms.CharField(label="Event Description")
        registration_deadline = forms.DateTimeField(
            label="Registration Deadline",
        )
        event_poster = forms.URLField(label="Event Poster URL")
        fields = [
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
            "event_author": forms.HiddenInput(),
        }
