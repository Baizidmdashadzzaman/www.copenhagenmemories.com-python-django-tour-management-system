from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from accounts.models import BlogPost, Category
from .forms_additions import BlogPostForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_blogpost')
def blog_list(request):
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    
    posts = BlogPost.objects.select_related('author', 'category').all()
    
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(title_dk__icontains=search_query) |
            Q(slug__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    if status:
        posts = posts.filter(status=status)
    
    if category:
        posts = posts.filter(category_id=category)
    
    posts = posts.order_by('-published_at', '-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/blog/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
        'category': category,
        'status_choices': BlogPost._meta.get_field('status').choices,
        'categories': Category.objects.all()
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_blogpost')
def blog_detail(request, pk):
    post = get_object_or_404(BlogPost.objects.select_related('author', 'category'), pk=pk)
    
    return render(request, 'accounts/admin/blog/detail.html', {
        'post': post
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_blogpost')
def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('blog_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm()

    return render(request, 'accounts/admin/blog/form.html', {'form': form, 'title': 'Create Blog Post', 'categories': Category.objects.all()})


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_blogpost')
def blog_edit(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('blog_detail', pk=post.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'accounts/admin/blog/form.html', {'form': form, 'post': post, 'title': 'Edit Blog Post', 'categories': Category.objects.all()})


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_blogpost')
def blog_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        try:
            post.delete()
            messages.success(request, 'Blog post deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting blog post: {str(e)}')
        return redirect('blog_list')

    return render(request, 'accounts/admin/blog/delete_confirm.html', {'post': post})


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_blogpost')
def blog_status_update(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(BlogPost._meta.get_field('status').choices):
            post.status = new_status
            if new_status == 'published' and not post.published_at:
                from django.utils import timezone
                post.published_at = timezone.now()
            post.save()
            messages.success(request, f'Blog post status updated to {new_status}!')
            return redirect('blog_detail', pk=post.pk)
        else:
            messages.error(request, 'Invalid status!')
    
    return render(request, 'accounts/admin/blog/status_update.html', {
        'post': post,
        'status_choices': BlogPost._meta.get_field('status').choices
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_blogpost')
def blog_feature_toggle(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    post.is_featured = not post.is_featured
    post.save()
    messages.success(request, f'Blog post {"featured" if post.is_featured else "unfeatured"} successfully!')
    return redirect('blog_detail', pk=post.pk)
