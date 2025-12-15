from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import CustomerReviewStatic, TourReview
from .forms import CustomerReviewStaticForm
from .decorators import permission_required_with_message
from .forms_additions import TourReviewForm

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_customerreviewstatic')
def review_list(request):
    search_query = request.GET.get('search', '')
    reviews = CustomerReviewStatic.objects.all()
    
    if search_query:
        reviews = reviews.filter(
            Q(name__icontains=search_query) | 
            Q(address__icontains=search_query) |
            Q(review__icontains=search_query)
        )
    
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/reviews/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_customerreviewstatic')
def review_create(request):
    if request.method == 'POST':
        form = CustomerReviewStaticForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review created successfully!')
            return redirect('review_list')
    else:
        form = CustomerReviewStaticForm()
    
    return render(request, 'accounts/admin/reviews/form.html', {'form': form, 'title': 'Create Review'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_customerreviewstatic')
def review_edit(request, pk):
    review = get_object_or_404(CustomerReviewStatic, pk=pk)
    
    if request.method == 'POST':
        form = CustomerReviewStaticForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('review_list')
    else:
        form = CustomerReviewStaticForm(instance=review)
    
    return render(request, 'accounts/admin/reviews/form.html', {
        'form': form,
        'title': 'Edit Review',
        'review': review
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_customerreviewstatic')
def review_delete(request, pk):
    review = get_object_or_404(CustomerReviewStatic, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return redirect('review_list')
    return render(request, 'accounts/admin/reviews/confirm_delete.html', {'review': review})

# Tour Review Views
@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tourreview')
def tour_review_list(request):
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    rating_filter = request.GET.get('rating', '')
    
    reviews = TourReview.objects.select_related('tour', 'customer', 'booking').all()
    
    if search_query:
        reviews = reviews.filter(
            Q(tour__title__icontains=search_query) |
            Q(customer__user__username__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(review__icontains=search_query)
        )
    
    if status:
        reviews = reviews.filter(status=status)
    
    if rating_filter:
        reviews = reviews.filter(overall_rating=int(rating_filter))
    
    reviews = reviews.order_by('-created_at')
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/tour_reviews/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
        'rating_filter': rating_filter,
        'status_choices': TourReview._meta.get_field('status').choices,
        'rating_choices': [(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tourreview')
def tour_review_detail(request, pk):
    review = get_object_or_404(TourReview.objects.select_related('tour', 'customer__user', 'booking'), pk=pk)
    
    return render(request, 'accounts/admin/tour_reviews/detail.html', {
        'review': review
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourreview')
def tour_review_status_update(request, pk):
    review = get_object_or_404(TourReview, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(TourReview._meta.get_field('status').choices):
            review.status = new_status
            review.save()
            messages.success(request, f'Review status updated to {new_status}!')
            return redirect('tour_review_detail', pk=review.pk)
        else:
            messages.error(request, 'Invalid status!')
    
    return render(request, 'accounts/admin/tour_reviews/status_update.html', {
        'review': review,
        'status_choices': TourReview._meta.get_field('status').choices
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourreview')
def tour_review_feature_toggle(request, pk):
    review = get_object_or_404(TourReview, pk=pk)
    review.is_featured = not review.is_featured
    review.save()
    messages.success(request, f'Review {"featured" if review.is_featured else "unfeatured"} successfully!')
    return redirect('tour_review_detail', pk=review.pk)

