from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from .utils import paginate_queryset
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.db.models import Count


def index(request):
    posts = (
        Post.objects.select_related('author', 'location', 'category')
        .filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    page_obj = paginate_queryset(request, posts)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(
            Post.objects.select_related('author', 'location', 'category'),
            pk=post_id
        )
        if post.author != request.user and (not post.is_published or
                                            post.pub_date > timezone.now() or
                                            not post.category.is_published):
            return render(request, 'pages/404.html', status=404)
    else:
        post = get_object_or_404(
            Post.objects.select_related('author', 'location', 'category'),
            pk=post_id,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    comments = post.comments.all()

    form = None
    if request.user.is_authenticated:
        form = CommentForm()

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = (
        Post.objects.select_related('author', 'location', 'category')
        .filter(
            category=category,
            is_published=True,
            pub_date__lte=timezone.now()
        )
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    page_obj = paginate_queryset(request, posts)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост успешно создан!')
            return redirect('profile', username=request.user.username)
    else:
        form = PostForm()

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('post_detail', post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост успешно обновлен!')
            return redirect('post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('post_detail', post_id=post_id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост успешно удален!')
        return redirect('profile', username=request.user.username)

    return render(request, 'blog/create.html', {'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Комментарий добавлен!')

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('post_detail', post_id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий обновлен!')
            return redirect('post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
        'post': comment.post
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий удален!')
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {'comment': comment})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile', username=request.user.username)
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})
