from django.urls import path

from events import views

app_name = "events"

urlpatterns = [
    path("", views.events_home, name="events-root-home"),
    path("<str:uid>home", views.events_home, name="events-home"),
    path("<str:uid>home/newevent", views.newevent, name="newevent"),
    path("<str:uid>home/allevent", views.allevent, name="allevent"),
    path("<str:uid>home/delevent<str:eid>", views.deleteevent, name="deleteevent"),
    path("<str:uid>home/explore", views.explore, name="explore"),
    path("explore", views.explore, name="explore"),
    path("event/participate/", views.ParticipateView, name="event-participate"),
    path("<str:uid>home/viewpart<str:eid>", views.viewparticipant, name="viewparticipant"),
    path("viewpart<str:eid>", views.viewparticipant, name="public-viewparticipant"),
]
