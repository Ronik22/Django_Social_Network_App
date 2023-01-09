import django_tables2 as tables

from events.models import Event


class EventsTable(tables.Table):
    participants_count: tables.Column = tables.Column(
        linkify=(
            "events:public-viewparticipant",
            {
                "eid": tables.A("event_id"),
            },
        ),
    )

    event_description: tables.TemplateColumn = tables.TemplateColumn(
        '<data-toggle="tooltip" title="{{record.event_description}}">{{record.event_description|truncatewords:5}}'  # noqa
    )

    event_name: tables.Column = tables.Column(
        linkify=(
            "events:public-viewparticipant",
            {
                "eid": tables.A("event_id"),
            },
        ),
    )

    class Meta:
        model = Event
        exclude: tuple[str] = ("event_id", "id", "event_poster", "host_name", "event_author")
        attrs: dict[str, str] = {"class": "table"}
        sequence = (
            "event_name",
            "event_start",
            "event_end",
            "registration_deadline",
            "event_description",
            "participants_count",
        )
