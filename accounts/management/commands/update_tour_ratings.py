from django.core.management.base import BaseCommand
from django.db.models import Avg, Count
from accounts.models import Tour

class Command(BaseCommand):
    help = 'Updates average rating and total reviews for all tours'

    def handle(self, *args, **kwargs):
        tours = Tour.objects.all()
        count = 0
        for tour in tours:
            reviews = tour.reviews.filter(status='approved')
            stats = reviews.aggregate(
                avg_rating=Avg('overall_rating'),
                review_count=Count('id')
            )
            
            tour.average_rating = stats['avg_rating'] or 0
            tour.total_reviews = stats['review_count'] or 0
            tour.save(update_fields=['average_rating', 'total_reviews'])
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated ratings for {count} tours'))
