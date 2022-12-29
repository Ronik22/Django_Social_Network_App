import logging

import django_tables2 as tables
from django.conf import settings  # noqa: F401
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.template import Context, Template  # noqa: F401
from django.utils import timezone

from events.forms import NewEventForm
from events.models import Event, Participant
from users.models import Profile

# from twilio.rest import Client

partlst = []  # global list for displaying participants for a particular event on home page
flag = 0  # boolean variable for deciding whether to display participants or not on home page
MAX_EVENT_SUMMARY_DISPLAY_COUNT = 2


class EventsTable(tables.Table):
    class Meta:
        model = Event
        exclude = ("event_id", "event_participants", "event_poster")
        attrs = {"class": "table"}


def get_caller_username(request) -> str:
    username: str = ""
    if request.user.is_authenticated:
        username = request.user.username
    return username


# Create your views here.
@login_required
def events_home(request, uid=""):
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
    if userobj.relationship_status == "single_male" and not userobj.relationship_status_override:
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
            if username in event.event_participants.split(","):
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

    owned_table = EventsTable(
        Event.objects.filter(event_author__user__username__icontains=username)
    )
    participating_table = EventsTable(Event.objects.filter(event_participants__icontains=username))

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
    form = NewEventForm(request.POST)
    if not uid:
        uid = request.user.id
    if request.method == "POST":
        if not request.user.is_staff:
            raise PermissionDenied()

        form.instance.event_author = Profile.objects.get(id=uid)

        if form.is_valid():
            event_start = form.cleaned_data.get("event_start")
            event_end = form.cleaned_data.get("event_end")
            registration_deadline = form.cleaned_data.get("registration_deadline")

            # for all_users in Profile.objects.all():
            #     if all_users.user.username == get_caller_username(request):
            #         uname = all_users.user.first_name
            #         umail = all_users.user.email
            #     else:
            #         uname = ""
            #         umail = ""

            # validation logic for event dates and times
            # dtnow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            dtnow = timezone.now()

            if event_end < dtnow or event_end < dtnow:
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Start date or end date can't be before current date",
                        "uid": request.user.id,
                        "form": form,
                    },
                )
            if event_start > event_end:
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Start date must be before end date",
                        "uid": request.user.id,
                        "form": form,
                    },
                )

            if registration_deadline > event_start or registration_deadline < dtnow:
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Deadline date must be before end date or after current date.",
                        "uid": request.user.id,
                        "form": form,
                    },
                )
            if registration_deadline == dtnow and registration_deadline <= dtnow:
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Deadline time must be after current time.",
                        "uid": request.user.id,
                        "form": form,
                    },
                )

            form.save()
            # redirect to home page once event is created
            return redirect("event_manager_home:events-root-home")
        else:
            return render(
                request,
                "createevent.html",
                {
                    "message": "Event form failed validation.",
                    "uid": request.user.id,
                    "form": form,
                },
            )
    else:
        # if uid != "" and uid not in request.session:
        #     raise PermissionDenied()
        # if uid != "" and request.session[uid] != uid:
        #     raise PermissionDenied()
        return render(request, "createevent.html", {"uid": request.user.id, "form": form})


@login_required
def allevent(request, uid=""):
    if not uid:
        uid = request.user.id
    # if uid != "" and uid not in request.session:
    #     raise PermissionDenied()
    # if uid != "" and request.session[uid] != uid:
    #     raise PermissionDenied()
    expired_event_id_list: list[Event] = []
    all_events_list: list[Event] = []
    userobj = Profile.objects.get(id=uid)
    uname = userobj.user.first_name
    umail = userobj.user.email

    if userobj.relationship_status == "single_male" and not userobj.relationship_status_override:
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
def deleteevent(request, uid="", event_id=""):
    if not uid:
        uid = request.user.id
    if not request.user.is_staff:
        raise PermissionDenied()

    # find the event which has to be deleted in database and delete it
    for all_events in Event.objects.all():
        if all_events.event_id == event_id:
            all_events.delete()

    # also delete the participants of that corresponding event
    for all_participants in Participant.objects.all():
        if all_participants.pevent_id == event_id:
            all_participants.delete()
    return redirect(events_home, uid=uid)


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

    userobj = Profile.objects.get(id=uid)
    uname = userobj.user.first_name
    umail = userobj.user.email

    if userobj.relationship_status == "single_male" and not userobj.relationship_status_override:
        raise PermissionDenied()  # This is the criteria to block on events per Gary

    curr_dt = timezone.now()
    for all_events in Event.objects.all():
        if all_events.event_start < curr_dt:
            expired_eventid_lst.append(all_events.event_id)
            all_events.delete()
    for ids in expired_eventid_lst:
        for all_participants in Participant.objects.all():
            if all_participants.pevent_id == ids:
                all_participants.delete()
    for all_events in Event.objects.all():
        exp.append(all_events)
    exp.sort(key=lambda eve: eve.event_start)
    return render(
        request,
        "explorepage.html",
        {"explst": exp, "uid": uid, "uname": uname, "umail": umail, "curr_dt": curr_dt},
    )


@login_required
def participate(request, uid="", eid=""):
    if not uid:
        uid = request.user.id
    username = get_caller_username(request)
    event = Event.objects.get(event_id=eid)
    event_participants: list[str] = event.event_participants.split(",")
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

    # if uid != "" and uid not in request.session:
    #     raise PermissionDenied()
    # if uid != "" and request.session[uid] != uid:
    #     raise PermissionDenied()
    # clear the list everytime the user requests for participant information
    partlst.clear()
    global flag
    flag = 1
    user = Profile.objects.get(id=uid)

    if eid in user.participating_events:
        partlst.append(user)

    return redirect("event_manager_home:events-root-home")
