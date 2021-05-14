from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def pagination(request, objects):
    """Рутина подготовки Пагинатора для страниц.

    аргументы:
    request - HttpRequest от запрошенной страницы, содержит номер страницы,
              для которой нужно вывести порцию объектов
    objects - набор объектов, которые надо разбить постранично
    return - порция объектов для номера страницы из request
    """
    paginator = Paginator(objects, settings.PAGINATOR_DEFAULT_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page


def index(request):
    post_list = Post.objects.all()
    page = pagination(request, post_list)
    return render(
        request,
        'posts/index.html',
        {'page': page},
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page = pagination(request, post_list)

    return render(request, 'posts/group.html', {'group': group, 'page': page})


def group_index(request):
    groups_list = Group.objects.all()
    page = pagination(request, groups_list)
    return render(request, 'posts/group_index.html',
                  {'groups': groups_list, 'page': page})


@login_required
def new_post(request):
    """For post-obj create form, render and check it, then save model-obj."""
    # initialise PostForm() with 'None' if request.POST absent
    form = PostForm(request.POST or None)

    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('index')

    return render(request, 'posts/new_post.html',
                  {'form': form, 'edit_flag': False})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    user_posts = profile_user.posts.all()
    page = pagination(request, user_posts)

    return render(request, 'posts/profile.html',
                  {'profile_user': profile_user,
                   'page': page})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    return render(request, 'posts/post.html',
                  {'post': post, 'author': post.author})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author != request.user:
        return redirect('post', username=username,
                        post_id=post_id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post.save()
        return redirect('post', username=post.author.username,
                        post_id=post_id)

    return render(request, 'posts/new_post.html',
                  {'form': form, 'edit_flag': True})
