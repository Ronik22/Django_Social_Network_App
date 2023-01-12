import random
from itertools import chain
from typing import Any, Optional, Union

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Model, Q
from django.db.models.manager import BaseManager
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from blog.utils import is_ajax
from events.models import Event
from notification.models import Notification
from users.models import Profile

from .forms import CommentForm
from .models import Comment, Post
from .utils import is_user_verified  # noqa: F401

""" Home page with all posts """


def first(request) -> HttpResponse:
    context: dict[str, BaseManager[Post]] = {"posts": Post.objects.all()}
    if request.user.is_authenticated:
        userobj = Profile.objects.get(id=request.user.id)
        if not userobj.verified:
            return redirect("profile")

    return render(request, "blog/first.html", context)


""" Posts of following user profiles """


@login_required
def posts_of_following_profiles(request) -> HttpResponse:

    profile: Profile = Profile.objects.get(user=request.user)
    users: list[User] = [user for user in profile.following.all()]
    posts: list[Post] = []
    qs: str = None
    for u in users:
        p: Profile = Profile.objects.get(user=u)
        p_posts = p.user.post_set.all()
        posts.append(p_posts)
    my_posts = profile.profile_posts()
    posts.append(my_posts)
    if len(posts) > 0:
        qs = sorted(chain(*posts), reverse=True, key=lambda obj: obj.date_posted)

    paginator: Paginator = Paginator(qs, 5)
    page = request.GET.get("page")
    try:
        posts_list = paginator.page(page)
    except PageNotAnInteger:
        posts_list = paginator.page(1)
    except EmptyPage:
        posts_list = paginator.page(paginator.num_pages)

    return render(request, "blog/feeds.html", {"profile": profile, "posts": posts_list})


""" Post Like """


@login_required
def LikeView(request) -> Optional[JsonResponse]:

    post: Post = get_object_or_404(Post, id=request.POST.get("id"))
    liked: bool = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
        notify: BaseManager[Notification] = Notification.objects.filter(
            post=post, sender=request.user, notification_type=1
        )
        notify.delete()
    else:
        post.likes.add(request.user)
        liked = True
        notify = Notification(post=post, sender=request.user, user=post.author, notification_type=1)
        notify.save()

    context: dict[str, Any] = {
        "post": post,
        "total_likes": post.total_likes(),
        "liked": liked,
    }

    if is_ajax(request=request):
        html: str = render_to_string("blog/like_section.html", context, request=request)
        return JsonResponse({"form": html})


""" Post save """


@login_required
def SaveView(request) -> Optional[JsonResponse]:

    post: Post = get_object_or_404(Post, id=request.POST.get("id"))
    saved: bool = False
    if post.saves.filter(id=request.user.id).exists():
        post.saves.remove(request.user)
        saved = False
    else:
        post.saves.add(request.user)
        saved = True

    context: dict[str, Any] = {
        "post": post,
        "total_saves": post.total_saves(),
        "saved": saved,
    }

    if is_ajax(request=request):
        html: str = render_to_string("blog/save_section.html", context, request=request)
        return JsonResponse({"form": html})


""" Like post comments """


@login_required
def LikeCommentView(request) -> Optional[JsonResponse]:
    # , id1, id2              id1=post.pk id2=reply.pk
    post: Comment = get_object_or_404(Comment, id=request.POST.get("id"))
    cliked: bool = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        cliked = False
    else:
        post.likes.add(request.user)
        cliked = True

    cpost: Post = get_object_or_404(Post, id=request.POST.get("pid"))
    total_comments2 = cpost.comments.all().order_by("-id")
    total_comments = cpost.comments.all().filter(reply=None).order_by("-id")
    tcl = {}
    for cmt in total_comments2:
        total_clikes = cmt.total_clikes()  # noqa: F841
        cliked = False
        if cmt.likes.filter(id=request.user.id).exists():
            cliked = True

        tcl[cmt.id] = cliked

    context: dict[str, Any] = {
        "comment_form": CommentForm(),
        "post": cpost,
        "comments": total_comments,
        "total_clikes": post.total_clikes(),
        "clikes": tcl,
    }

    if is_ajax(request=request):
        html: str = render_to_string("blog/comments.html", context, request=request)
        return JsonResponse({"form": html})


""" Home page with all posts """


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name: str = "blog/home.html"
    context_object_name: str = "posts"
    ordering: list[str] = ["-date_posted"]
    paginate_by: int = 5

    def get_context_data(self, *args, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super(PostListView, self).get_context_data()
        users: list[User] = list(User.objects.exclude(pk=self.request.user.pk))

        if len(users) > 3:
            cnt: int = 3
        else:
            cnt = len(users)
        random_users: list[User] = random.sample(users, cnt)
        context["random_users"] = random_users
        return context

    def render_to_response(self, context):
        userobj: Profile = Profile.objects.get(id=self.request.user.id)

        if not userobj.verified:
            return redirect("profile")

        return super(PostListView, self).render_to_response(context)


""" All the posts of the user """


class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name: str = "blog/user_posts.html"
    context_object_name: str = "posts"
    paginate_by: int = 5

    def get_queryset(self) -> BaseManager[Post]:
        user: User = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(author=user).order_by("-date_posted")


""" Post detail view """


@login_required
def PostDetailView(request, pk) -> Union[JsonResponse, HttpResponse]:

    stuff: Post = get_object_or_404(Post, id=pk)
    total_likes: int = stuff.total_likes()
    total_saves: int = stuff.total_saves()
    total_comments = stuff.comments.all().filter(reply=None).order_by("-id")
    total_comments2 = stuff.comments.all().order_by("-id")

    context = {}

    if request.method == "POST":
        comment_qs = None
        comment_form: CommentForm = CommentForm(request.POST or None)
        if comment_form.is_valid():
            form = request.POST.get("body")
            reply_id = request.POST.get("comment_id")
            if reply_id:
                comment_qs: Comment = Comment.objects.get(id=reply_id)

            comment: Comment = Comment.objects.create(
                name=request.user, post=stuff, body=form, reply=comment_qs
            )
            comment.save()
            if reply_id:
                notify: Notification = Notification(
                    post=stuff,
                    sender=request.user,
                    user=stuff.author,
                    text_preview=form,
                    notification_type=4,
                )
                notify.save()
            else:
                notify = Notification(
                    post=stuff,
                    sender=request.user,
                    user=stuff.author,
                    text_preview=form,
                    notification_type=3,
                )
                notify.save()
            total_comments = stuff.comments.all().filter(reply=None).order_by("-id")
            total_comments2 = stuff.comments.all().order_by("-id")
    else:
        comment_form = CommentForm()

    tcl = {}
    for cmt in total_comments2:
        total_clikes = cmt.total_clikes()  # noqa: F841
        cliked: bool = False
        if cmt.likes.filter(id=request.user.id).exists():
            cliked = True

        tcl[cmt.id] = cliked
    context["clikes"] = tcl

    liked: bool = False
    if stuff.likes.filter(id=request.user.id).exists():
        liked = True
    context["total_likes"] = total_likes
    context["liked"] = liked

    saved: bool = False
    if stuff.saves.filter(id=request.user.id).exists():
        saved = True
    context["total_saves"] = total_saves
    context["saved"] = saved

    context["comment_form"] = comment_form

    context["post"] = stuff
    context["comments"] = total_comments

    if is_ajax(request=request):
        html: str = render_to_string("blog/comments.html", context, request=request)
        return JsonResponse({"form": html})

    return render(request, "blog/post_detail.html", context)


""" Create post """


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields: list[str] = ["title", "content", "image"]

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)


""" Update post """


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields: list[str] = ["title", "content", "image"]

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self) -> bool:
        post: Model = self.get_object()
        if self.request.user == post.author:
            return True
        return False


""" Delete post """


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url: str = "/"

    def test_func(self) -> bool:
        post: Model = self.get_object()
        if self.request.user == post.author:
            return True
        return False


""" About page """


def about(request) -> HttpResponse:
    return render(request, "blog/about.html", {"title": "About"})


""" Search by post title or username """


@login_required
def search(request) -> HttpResponse:
    query = request.GET["query"]
    query_results = {}
    if len(query) >= 150 or len(query) < 1:
        query_results["posts"] = Post.objects.none()
    elif len(query.strip()) == 0:
        query_results["posts"] = Post.objects.none()
    else:
        allpostsTitle: BaseManager[Post] = Post.objects.filter(title__icontains=query)
        allpostsAuthor: BaseManager[Post] = Post.objects.filter(author__username=query)
        query_results["posts"] = allpostsAuthor.union(allpostsTitle)

        query_results["profiles"] = Profile.objects.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
        )

        query_results["events"] = Event.objects.filter(event_name__icontains=query)

    params: dict[str, BaseManager[Post]] = {"query_results": query_results}
    return render(request, "blog/search_results.html", params)


""" Liked posts """


@login_required
def AllLikeView(request) -> HttpResponse:
    user = request.user
    liked_posts = user.blogpost.all()
    context: dict[str, Any] = {"liked_posts": liked_posts}
    return render(request, "blog/liked_posts.html", context)


""" Saved posts """


@login_required
def AllSaveView(request) -> HttpResponse:
    user = request.user
    saved_posts = user.blogsave.all()
    context: dict[str, Any] = {"saved_posts": saved_posts}
    return render(request, "blog/saved_posts.html", context)
