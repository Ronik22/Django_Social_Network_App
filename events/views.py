import logging
from typing import Any, Optional

from django.conf import settings  # noqa: F401
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template import Context, Template  # noqa: F401
from django.template.loader import render_to_string
from django.utils import timezone

from blog.utils import is_ajax
from events.forms import NewEventForm
from events.models import Event, Participant
from events.tables import EventsTable
from notification.models import Notification  # noqa: F401
from users.models import Profile

# from twilio.rest import Client

partlst = []  # global list for displaying participants for a particular event on home page
flag = 0  # boolean variable for deciding whether to display participants or not on home page
MAX_EVENT_SUMMARY_DISPLAY_COUNT = 2
RELATIONSHIP_BLOCKLIST: list[str] = ["single_male", "single_female"]


def get_caller_username(request) -> str:
    username: str = ""
    if request.user.is_authenticated:
        username = request.user.username
    return username


# Create your views here.
@login_required
def events_home(request, uid="") -> HttpResponse:
    if not uid:
        uid: str = request.user.id
    username: str = get_caller_username(request)
    all_events = Event.objects.all().order_by("event_start")

    participating_event_list: list[Event] = []
    owned_event_list: list[Event] = []
    expired_eventid_lst: list[Event] = []

    # assign additional info to display on webpage
    umail = ""
    userobj: Profile = Profile.objects.get(id=uid)
    umail = userobj.user.email
    if (
        userobj.relationship_status in RELATIONSHIP_BLOCKLIST
        and not userobj.relationship_status_override
    ):
        raise PermissionDenied()  # This is the criteria to block on events per Gary

    # automatically remove events from the database which are ongoing or are finished
    curr_dt = timezone.now()
    for event in all_events:
        if event.event_start < curr_dt:
            expired_eventid_lst.append(event.event_id)
            event.delete()

    # collect the events in which user has participated or is the owner
    for event in all_events:
        logging.debug(f"{event.event_details=}")
        logging.debug(f"{event.event_participants=}")
        for _ in range(0, MAX_EVENT_SUMMARY_DISPLAY_COUNT):
            if username in event.event_participants.all():
                participating_event_list.append(event)

    for event in all_events:
        for _ in range(0, MAX_EVENT_SUMMARY_DISPLAY_COUNT):
            if event.event_author == username:
                owned_event_list.append(event)

    # sorting the list according to start dates
    owned_event_list.sort(key=lambda eve: eve.event_start)
    participating_event_list.sort(key=lambda eve: eve.event_start)

    logging.debug(f"{owned_event_list=}")
    logging.debug(f"{participating_event_list=}")

    owned_table = EventsTable(Event.objects.filter(event_author__user__id=uid))
    participating_table = EventsTable(Event.objects.filter(event_participants__id=uid))

    return render(
        request,
        "home.html",
        {
            "uname": username,
            "owned_event_list": owned_event_list,
            "participating_event_list": participating_event_list,
            "owned_table": owned_table,
            "participating_table": participating_table,
            "uid": uid,
            "umail": umail,
        },
    )


@login_required
def newevent(request, uid=""):
    if not uid:
        uid = request.user.id
    if request.method == "POST":
        if not request.user.is_staff:
            raise PermissionDenied()

        form: NewEventForm = NewEventForm(request.POST, request.FILES)

        form.instance.event_author = Profile.objects.get(id=uid)

        if form.is_valid():
            event_start = form.cleaned_data.get("event_start")
            event_end = form.cleaned_data.get("event_end")
            registration_deadline = form.cleaned_data.get("registration_deadline")

            # validation logic for event dates and times
            # dtnow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            dtnow = timezone.now()

            if event_end < dtnow or event_end < dtnow:
                logging.error(
                    "Start date or end date can't be before current date" f"{form.fields=}"
                )
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Start date or end date can't be before current date",
                        "uid": uid,
                        "form": form,
                    },
                )
            if event_start > event_end:
                logging.error("Start date must be before end date" f"{form.fields=}")
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Start date must be before end date",
                        "uid": uid,
                        "form": form,
                    },
                )

            if registration_deadline > event_start or registration_deadline < dtnow:
                logging.error(
                    "Deadline date must be before end date or after current date." f"{form.fields=}"
                )
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Deadline date must be before end date or after current date.",
                        "uid": uid,
                        "form": form,
                    },
                )
            if registration_deadline == dtnow and registration_deadline <= dtnow:
                logging.error("Deadline time must be after current time." f"{form.fields=}")
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Deadline time must be after current time.",
                        "uid": uid,
                        "form": form,
                    },
                )

            form.save()
            logging.info(f"Event Created: {form.fields}")
            # redirect to home page once event is created
            messages.success(request, "Successfully Created Event!")
            return render(request, "createevent.html", {"uid": uid, "form": NewEventForm()})
        else:
            logging.error(f"Failed to save form data with errors: {form.errors}")
            return render(
                request,
                "createevent.html",
                {
                    "message": "Event form failed validation.",
                    "uid": uid,
                    "form": form,
                },
            )
    else:
        return render(request, "createevent.html", {"uid": uid, "form": NewEventForm()})


@login_required
def allevent(request, uid=""):
    if not uid:
        uid = request.user.id

    expired_event_id_list: list[Event] = []
    all_events_list: list[Event] = []
    userobj = Profile.objects.get(id=uid)
    uname = userobj.user.first_name
    umail = userobj.user.email

    if (
        userobj.relationship_status in RELATIONSHIP_BLOCKLIST
        and not userobj.relationship_status_override
    ):
        raise PermissionDenied()  # This is the criteria to block on events per Gary

    for events in Event.objects.all():
        all_events_list.append(events)

    # automatically remove events from the database which are ongoing or are finished and their
    # corresponding participants
    curr_dt = timezone.now()
    for event in all_events_list:
        if event.event_start < curr_dt:
            expired_event_id_list.append(event.event_id)
            all_events_list.pop(event)

    # simultaneously remove the participants of these events from participant database
    for ids in expired_event_id_list:
        for all_participants in Participant.objects.all():
            if all_participants.pevent_id == ids:
                all_participants.delete()

    # collect the events in which user has participated or is the host

    # sort the list according to start dates
    all_events_list.sort(key=lambda eve: eve.event_start)
    logging.debug(f"{all_events_list=}")
    return render(
        request,
        "allevents.html",
        {"uname": uname, "alleventlist": all_events_list, "uid": uid, "umail": umail},
    )


@login_required
def deleteevent(request, uid="", eid=""):
    if not uid:
        uid = request.user.id

    if not request.user.is_staff:
        # if not event.event_author == username:
        raise PermissionDenied()

    # find the event which has to be deleted in database and delete it
    for all_events in Event.objects.all():
        if all_events.event_id == eid:
            all_events.delete()

    # also delete the participants of that corresponding event
    for all_participants in Participant.objects.all():
        if all_participants.pevent_id == eid:
            all_participants.delete()
    return events_home(request, uid=uid)


@login_required
def explore(request, uid=""):
    if not uid:
        uid = request.user.id
    # if uid != "" and uid not in request.session:
    #     raise PermissionDenied()
    # if uid != "" and request.session[uid] != uid:
    #     raise PermissionDenied()
    exp = []
    expired_eventid_lst = []
    participation_list = []

    userobj = Profile.objects.get(id=uid)
    uname = userobj.user.first_name
    umail = userobj.user.email

    if (
        userobj.relationship_status in RELATIONSHIP_BLOCKLIST
        and not userobj.relationship_status_override
    ):
        raise PermissionDenied()  # This is the criteria to block on events per Gary

    curr_dt = timezone.now()
    for all_events in Event.objects.all():
        if all_events.event_start < curr_dt:
            expired_eventid_lst.append(all_events.event_id)
            all_events.delete()

    for event in Event.objects.all():
        exp.append(event)

    exp.sort(key=lambda eve: eve.event_start)

    for event in exp:
        if is_user_participating(event.pk, userobj.user.id):
            participation_list.append(event.pk)

    logging.debug(f"{participation_list=}")

    return render(
        request,
        "explorepage.html",
        {
            "explst": exp,
            "uid": uid,
            "uname": uname,
            "umail": umail,
            "curr_dt": curr_dt,
            "participation_list": participation_list,
        },
    )


@login_required
def participate(request, uid="", eid=""):
    if not uid:
        uid = request.user.id
    username = get_caller_username(request)
    event = Event.objects.get(event_id=eid)
    event_participants: list[str] = event.event_participants.all()
    logging.debug(f"Get participant {event.event_participants.get(id=uid)}")
    if username not in event_participants:
        messages.success(request, messages.INFO, f"Adding {username} to participant list!")
        logging.debug(f"Adding {username} to participant list for event ID {event.event_id}")
        event_participants.append(username)
        event.event_participants = event_participants
        event.save()
    else:
        messages.warning(request, f"{username} is already in participant list!")
        logging.debug(f"{username} is already in participant list for event ID {event.event_id}")
    return explore(request, uid=uid)


@login_required
def viewparticipant(request, uid="", eid=""):
    if not uid:
        uid = request.user.id

    event: Event = Event.objects.get(event_id=eid)

    logging.debug(f"{event.event_participants=}")

    participant_list: list[str] = event.event_participants.all()

    logging.debug(f"{participant_list=}")

    return render(
        request,
        "participant_list.html",
        {"participant_list": participant_list, "event": event},
    )


def is_user_participating(event_pk, user_id) -> bool:
    try:
        events = Event.objects.filter(event_participants__id=user_id)
    except Event.DoesNotExist:
        return False

    try:
        if events.get(pk=event_pk):
            logging.debug(f"{user_id} is participating in event {event_pk}")
            return True
        else:
            logging.debug(f"{user_id} is NOT participating in event {event_pk}")
            return False
    except ObjectDoesNotExist:
        return False


@login_required
def ParticipateView(request) -> Optional[JsonResponse]:
    userobj: Profile = Profile.objects.get(id=request.user.id)
    event_pk: str = request.POST.get("event_pk")

    event: Event = get_object_or_404(Event, pk=event_pk)
    participants = event.event_participants.all()

    if not userobj.verified:
        raise PermissionDenied()

    participating: bool = False
    if userobj in participants:
        logging.debug(f"Removing {userobj} from participants of event {event.pk}")
        event.event_participants.remove(userobj)
        participating = False
        # notify = Notification.objects.filter(post=event, sender=userobj, notification_type=1)
        # notify.delete()
    else:
        logging.debug(f"Adding {userobj} to participants of event {event.pk}")
        event.event_participants.add(userobj)
        participating = True
        # notify = Notification(
        #     post=event, sender=userobj, user=event.event_author, notification_type=1
        # )
        # notify.save()

    context: dict[str, Any] = {
        "event": event,
        "participating": participating,
    }

    if is_ajax(request=request):
        html: str = render_to_string("participate_section.html", context, request=request)
        logging.debug(html)
        return JsonResponse({"form": html})
