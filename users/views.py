from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

from friend.friend_request_status import FriendRequestStatus
from friend.models import FriendList, FriendRequest
from friend.utils import get_friend_request_or_false
from myproject import utils
from notification.models import Notification
from users.forms import ProfileUpdateForm, UserRegisterForm, UserUpdateForm
from users.models import Profile


@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs) -> None:
    user.profile.is_online = True
    user.profile.save()


@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs) -> None:
    user.profile.is_online = False
    user.profile.save()


""" Following and Unfollowing users """


@login_required
def follow_unfollow_profile(request):
    if request.method == "POST":
        my_profile = Profile.objects.get(user=request.user)
        pk = request.POST.get("profile_pk")
        obj = Profile.objects.get(pk=pk)

        if obj.user in my_profile.following.all():
            my_profile.following.remove(obj.user)
            notify = Notification.objects.filter(sender=request.user, notification_type=2)
            notify.delete()
        else:
            my_profile.following.add(obj.user)
            notify = Notification(sender=request.user, user=obj.user, notification_type=2)
            notify.save()
        return redirect(request.META.get("HTTP_REFERER"))
    return redirect("profile-list-view")


""" User account creation """


def register(request):
    if request.method == "POST":
        form: UserRegisterForm = UserRegisterForm(request.POST)
        if form.is_valid():
            """
            # reCAPTCHA V2
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()

            if result['success']:
            """
            if True:  # Shim this in to turn off captcha for now
                form.save()
                username: str = form.cleaned_data.get("username")
                user_email: str = form.cleaned_data.get("email")
                messages.success(
                    request, f"Your account has been created! You can login now {username}"
                )
                # message: str = f"New account creation for {username} has succeeded"

                utils.send_welcome_email(
                    user_email=user_email,
                    username=username,
                    profile_url=f"http://www.csctn.net/user/public-profile/{username}/",
                )

                utils.new_user_created_email(
                    user_email=user_email,
                    username=username,
                    profile_url=f"http://www.csctn.net/user/public-profile/{username}/",
                )

                return redirect("login")
            else:
                messages.error(request, "Invalid form data. Please try again.")

    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


""" User profile """


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated!")
            return redirect("profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"u_form": u_form, "p_form": p_form}

    return render(request, "users/profile.html", context)


""" Creating a public profile view """


def public_profile(request, username):
    user = User.objects.get(username=username)
    return render(request, "users/public_profile.html", {"cuser": user})


""" All user profiles """


class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "users/all_profiles.html"
    context_object_name = "profiles"
    paginate_by: int = 20

    def get_queryset(self):
        return Profile.objects.all().exclude(user=self.request.user)

    def render_to_response(self, context):
        userobj: Profile = Profile.objects.get(id=self.request.user.id)

        if not userobj.verified:
            return redirect("profile")

        return super(ProfileListView, self).render_to_response(context)


""" User profile details view """


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "users/user_profile_details.html"
    context_object_name = "profiles"

    def get_queryset(self):
        return Profile.objects.all().exclude(user=self.request.user)

    def get_object(self, **kwargs):
        pk = self.kwargs.get("pk")
        view_profile = Profile.objects.get(pk=pk)
        return view_profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        view_profile = self.get_object()
        my_profile = Profile.objects.get(user=self.request.user)
        if view_profile.user in my_profile.following.all():
            follow = True
        else:
            follow = False
        context["follow"] = follow

        # FRIENDS START

        account = view_profile.user
        try:
            friend_list = FriendList.objects.get(user=account)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=account)
            friend_list.save()
        friends = friend_list.friends.all()
        context["friends"] = friends

        is_self = True
        is_friend = False
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        friend_requests = None
        user = self.request.user
        if user.is_authenticated and user != account:
            is_self = False
            if friends.filter(pk=user.id):
                is_friend = True
            else:
                is_friend = False
                # CASE 1: request from them to you
                if get_friend_request_or_false(sender=account, receiver=user) is not False:
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context["pending_friend_request_id"] = get_friend_request_or_false(
                        sender=account, receiver=user
                    ).pk
                # CASE 2: request you sent to them
                elif get_friend_request_or_false(sender=user, receiver=account) is not False:
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
                # CASE 3: no request has been sent
                else:
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

        elif not user.is_authenticated:
            is_self = False
        else:
            try:
                friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
            except Exception:
                pass
        context["request_sent"] = request_sent
        context["is_friend"] = is_friend
        context["is_self"] = is_self
        context["friend_requests"] = friend_requests
        # FRIENDS END

        return context
