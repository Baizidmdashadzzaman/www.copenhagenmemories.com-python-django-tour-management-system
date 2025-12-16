
import random
from datetime import datetime, timedelta, time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from accounts.models import (
    Tour, TourSupplier, Category, DestinationRegion, City, Country,
    TourImage, TourHighlight, TourIncluded, TourExcluded,
    TourItinerary, TourRequirement, TourFAQ, TourPricing, TourSchedule
)

class Command(BaseCommand):
    help = 'Seeds the database with 10 dummy tours and related data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # 1. Ensure Prerequisites
        country, _ = Country.objects.get_or_create(
            name='Denmark',
            defaults={
                'code': 'DK',
                'currency_code': 'DKK',
                'currency_symbol': 'kr',
                'language': 'da'
            }
        )
        
        region, _ = DestinationRegion.objects.get_or_create(
            name='Copenhagen Region',
            defaults={'country': country}
        )
        
        city, _ = City.objects.get_or_create(
            name='Copenhagen',
            defaults={'country': country, 'region': region}
        )
        
        supplier, _ = TourSupplier.objects.get_or_create(
            company_name='Best Copenhagen Tours',
            defaults={'email': 'info@bestcph.com', 'country': country}
        )
        
        categories = ['Walking Tours', 'Boat Tours', 'Food Tours', 'Bike Tours']
        category_objs = []
        for cat_name in categories:
            cat, _ = Category.objects.get_or_create(name=cat_name)
            category_objs.append(cat)

        # 2. Create 10 Tours
        titles = [
             "Grand Canal Tour of Copenhagen",
             "Hidden Gems Culinary Walk",
             "Royal Palaces & Castles Day Trip",
             "Copenhagen Highlights by Bike",
             "Alternative Christiania Experience",
             "Viking History & Roskilde Museum",
             "Hygga & Happiness Walking Tour",
             "Jazz & Harbor Evening Cruise",
             "Design & Architecture Masterclass",
             "Tivoli Gardens VIP Access Tour"
        ]

        # Use an existing image if available as a placeholder
        dummy_image_path = 'tours/gallery/tours-07.jpg'

        for i, title in enumerate(titles):
            self.stdout.write(f'Creating tour: {title}')
            
            # Helper to generate a unique slug if needed, though get_or_create handles the first check
            base_slug = slugify(title)
            
            tour, created = Tour.objects.get_or_create(
                title=title,
                defaults={
                    'supplier': supplier,
                    'category': random.choice(category_objs),
                    'destination_region': region,
                    'city': city,
                    'slug': base_slug,
                    'short_description': f'Experience the best of {title} with our expert guides.',
                    'description': f'This is a detailed description for {title}. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
                    'duration_hours': Decimal(random.randint(2, 8)),
                    'min_participants': 1,
                    'max_participants': 20,
                    'base_price': Decimal(random.randint(200, 1500)),
                    'currency': 'DKK',
                    'meeting_point': 'City Hall Square, Copenhagen',
                    'start_date': datetime.now().date(),
                    'end_date': datetime.now().date() + timedelta(days=365),
                    'status': 'active',
                    'is_featured': random.choice([True, False]),
                    'average_rating': Decimal(random.uniform(4.0, 5.0)),
                    'total_reviews': random.randint(5, 100),
                    'main_image': dummy_image_path
                }
            )
            
            if not created:
                self.stdout.write(f'Tour {title} already exists. Skipping related data creation for this tour.')
                continue

            # 3. Create Related Data
            
            # Tour Images
            for img_idx in range(3):
                TourImage.objects.create(
                    tour=tour,
                    image=dummy_image_path,
                    caption=f'Scene {img_idx+1} from {title}',
                    display_order=img_idx
                )
            
            # Highlights
            for h in range(3):
                TourHighlight.objects.create(
                    tour=tour,
                    highlight=f'Highlight {h+1} for {title}: Amazing sights',
                    display_order=h
                )
            
            # Included/Excluded
            for inc in range(3):
                TourIncluded.objects.create(tour=tour, item=f'Included item {inc+1} (e.g. Guide)')
            for exc in range(2):
                TourExcluded.objects.create(tour=tour, item=f'Excluded item {exc+1} (e.g. Lunch)')
                
            # Itinerary
            for step in range(1, 4):
                TourItinerary.objects.create(
                    tour=tour,
                    step_number=step,
                    title=f'Step {step}: Exploration',
                    description=f'We will visit key location {step} and learn about its history.',
                    duration_minutes=45
                )
                
            # Requirements
            TourRequirement.objects.create(tour=tour, requirement='Comfortable walking shoes')
            TourRequirement.objects.create(tour=tour, requirement='Camera')
            
            # FAQs
            TourFAQ.objects.create(
                tour=tour,
                question='Is food included?',
                answer='Yes, light snacks are provided.'
            )
            TourFAQ.objects.create(
                tour=tour,
                question='Is it wheelchair accessible?',
                answer='Please check the tour details or contact us.'
            )
            
            # Pricing
            for p_type in ['adult', 'child']:
                price = tour.base_price if p_type == 'adult' else tour.base_price * Decimal('0.5')
                TourPricing.objects.create(
                    tour=tour,
                    participant_type=p_type,
                    price=price
                )
            
            # Schedules
            for day in range(1, 30, 2): # Every other day for next month
                date = datetime.now().date() + timedelta(days=day)
                TourSchedule.objects.create(
                    tour=tour,
                    date=date,
                    start_time=time(10, 0),
                    available_slots=20,
                    status='available'
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded 10 tours with related data.'))
