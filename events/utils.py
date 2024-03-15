from events.models import Event


def get_participants_count(event_pk: str) -> int:
    event: Event = Event.objects.get(pk=event_pk)
    return len(event.event_participants.all())
