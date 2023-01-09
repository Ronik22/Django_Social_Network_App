import django_tables2 as tables

from events.models import Event


class EventsTable(tables.Table):
    class Meta:
        model = Event
        exclude: tuple[str] = ("event_id", "event_participants", "event_poster")
        attrs: dict[str, str] = {"class": "table"}
