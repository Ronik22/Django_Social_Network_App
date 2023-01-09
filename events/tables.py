import django_tables2 as tables

from events.models import Event


class EventsTable(tables.Table):
    participants_count = tables.Column(
        linkify=(
            "events:public-viewparticipant",
            {
                "eid": tables.A("event_id"),
            },
        ),
    )

    class Meta:
        model = Event
        exclude: tuple[str] = ("event_id", "event_poster")
        attrs: dict[str, str] = {"class": "table"}
