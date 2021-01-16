from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Comment, Post
from .forms import CommentForm
from django.http import HttpResponseRedirect
from users.models import Profile
from itertools import chain
from django.contrib.auth.decorators import login_required


def home(request):
    context = {
        'posts':Post.objects.all()
    }
    return render(request, 'blog/home.html', context)

@login_required
def posts_of_following_profiles(request):
    profile = Profile.objects.get(user = request.user)
    users = [user for user in profile.following.all()]
    posts = []
    qs = None
    for u in users:
        p = Profile.objects.get(user=u)
        p_posts = p.user.post_set.all()
        posts.append(p_posts)
    my_posts = profile.profile_posts()
    posts.append(my_posts)
    if len(posts)>0:
        qs = sorted(chain(*posts), reverse=True, key=lambda obj:obj.date_posted)
    return render(request,'blog/feeds.html',{'profile':profile,'posts':qs})


@login_required
def LikeView(request, pk):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse('post-detail', args=[str(pk)]))

@login_required
def LikeCommentView(request, id1, id2):
    post = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    cliked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        cliked = False
    else:
        post.likes.add(request.user)
        cliked = True
    return HttpResponseRedirect(reverse('post-detail', args=[str(id1)]))


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, *args,**kwargs):
        context = super(PostDetailView, self).get_context_data()
        stuff = get_object_or_404(Post, id=self.kwargs['pk'])
        total_likes = stuff.total_likes()
        total_comments = stuff.comments.all()

        tcl={}
        for cmt in total_comments:
            total_clikes = cmt.total_clikes()
            cliked = False
            if cmt.likes.filter(id=self.request.user.id).exists():
                cliked = True

            tcl[cmt.id] = cliked

        context["clikes"]=tcl

        liked = False
        if stuff.likes.filter(id=self.request.user.id).exists():
            liked = True

        context["total_likes"]=total_likes
        context["liked"]=liked
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields =['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


@login_required
def add_comment(request, pk):
    form = request.POST.get('body')
    if request.method == "POST":
        user = request.user
        post = get_object_or_404(Post, pk=pk)
        
        comment = Comment(name=user,post=post,body=form)
        comment.save() 
        return redirect('post-detail', post.id)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment.html', {'form': form})





class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields =['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    return render(request, 'blog/about.html', {'title':'About'})
