from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import TourReview, Tour

@receiver(post_save, sender=TourReview)
@receiver(post_delete, sender=TourReview)
def update_tour_rating(sender, instance, **kwargs):
    tour = instance.tour
    reviews = tour.reviews.filter(status='approved')
    
    stats = reviews.aggregate(
        avg_rating=Avg('overall_rating'),
        count=Count('id')
    )
    
    tour.average_rating = stats['avg_rating'] or 0
    tour.total_reviews = stats['count'] or 0
    tour.save(update_fields=['average_rating', 'total_reviews'])
