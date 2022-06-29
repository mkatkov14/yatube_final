# posts/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Follow, Group, Post
from .utils import get_page_obj

POSTS_COUNT: int = 10

User = get_user_model()


def index(request):
    """"Главная страница."""
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    page_obj = get_page_obj(request, posts, POSTS_COUNT)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Группы."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page_obj(request, posts, POSTS_COUNT)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Страница пользователя."""
    author = get_object_or_404(User, username=username)
    following = (request.user.is_authenticated
                 and author.following.filter(user=request.user).exists())
    posts = author.posts.all()
    page_obj = get_page_obj(request, posts, POSTS_COUNT)
    template = 'posts/profile.html'
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница поста."""
    post = get_object_or_404(Post, id=post_id)
    count = Post.objects.filter(author_id=post.author_id).count()
    template = 'posts/post_detail.html'
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'count': count,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Новый пост."""
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактировать пост."""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Новый комментарий."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Подписки текущего пользователя."""
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page_obj(request, posts, POSTS_COUNT)
    return render(request, 'posts/follow.html', {'page_obj': page_obj})


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Дизлайк, отписка."""
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user,
        author=author,
    )
    follow.delete()
    return redirect('posts:profile', username=username)
