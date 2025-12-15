from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import (
    Country, DestinationRegion, Category, Tour, City, Coupon, 
    BlogPost, Booking, Payment, Newsletter, ContactUs, CustomerReviewStatic,
    Slider, Page, Customer, TourSupplier,
    TourIncluded, TourExcluded, TourItinerary, TourRequirement, 
    TourFAQ, TourPricing, TourSchedule, TourBlackoutDate
)
from django.contrib.auth.models import User
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate demo data for all models'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting demo data population...'))

        # Create or get superuser
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@yourtourguide.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if _ and not admin_user.has_usable_password():
            admin_user.set_password('admin123')
            admin_user.save()

        # Create demo user
        demo_user, _ = User.objects.get_or_create(
            username='demouser',
            defaults={
                'email': 'demo@yourtourguide.com',
                'first_name': 'Demo',
                'last_name': 'User',
            }
        )
        if _:
            demo_user.set_password('demo123')
            demo_user.save()

        # Countries
        denmark, _ = Country.objects.get_or_create(
            name='Denmark',
            defaults={'code': 'DK', 'is_active': True}
        )
        sweden, _ = Country.objects.get_or_create(
            name='Sweden',
            defaults={'code': 'SE', 'is_active': True}
        )
        self.stdout.write(self.style.SUCCESS('✓ Countries created'))

        # Cities
        copenhagen, _ = City.objects.get_or_create(
            name='Copenhagen',
            defaults={
                'name_dk': 'København',
                'country': denmark,
                'is_active': True,
                'description': 'The capital of Denmark with beautiful canals and historic architecture.'
            }
        )
        aarhus, _ = City.objects.get_or_create(
            name='Aarhus',
            defaults={
                'name_dk': 'Aarhus',
                'country': denmark,
                'is_active': True,
                'description': 'Denmark\'s second largest city known for culture and Viking history.'
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Cities created'))

        # Categories
        culture, _ = Category.objects.get_or_create(
            name='Culture',
            defaults={
                'name_dk': 'Kultur',
                'status': 'active',
                'description': 'Cultural tours and experiences'
            }
        )
        adventure, _ = Category.objects.get_or_create(
            name='Adventure',
            defaults={
                'name_dk': 'Eventyr',
                'status': 'active',
                'description': 'Adventure and outdoor activities'
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Categories created'))

        # Tours
        # First create a tour supplier if needed
        supplier, _ = TourSupplier.objects.get_or_create(
            company_name='Demo Tours',
            defaults={
                'email': 'supplier@demotours.com',
                'phone': '+4540123456',
                'verified': True
            }
        )
        
        tour1, _ = Tour.objects.get_or_create(
            title='Copenhagen City Tour',
            defaults={
                'supplier': supplier,
                'title_dk': 'København bytur',
                'category': culture,
                'city': copenhagen,
                'base_price': Decimal('49.99'),
                'currency': 'DKK',
                'duration_hours': Decimal('3'),
                'description': 'Explore the highlights of Copenhagen with our experienced guide.',
                'description_dk': 'Udforsk højdepunkterne i København med vores erfarne guide.',
                'max_participants': 20,
                'status': 'active',
                'is_featured': True,
            }
        )
        
        tour2, _ = Tour.objects.get_or_create(
            title='Aarhus Viking Adventure',
            defaults={
                'supplier': supplier,
                'title_dk': 'Aarhus Viking Eventyr',
                'category': adventure,
                'city': aarhus,
                'base_price': Decimal('59.99'),
                'currency': 'DKK',
                'duration_hours': Decimal('4'),
                'description': 'Experience Viking history and culture in Aarhus.',
                'description_dk': 'Oplev vikinghistorie og kultur i Aarhus.',
                'max_participants': 25,
                'status': 'active',
                'is_featured': False,
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Tours created'))

        # Tour Included Items
        TourIncluded.objects.get_or_create(
            tour=tour1,
            item='Professional Guide',
            defaults={'item_dk': 'Professionel guide', 'display_order': 1}
        )
        TourIncluded.objects.get_or_create(
            tour=tour1,
            item='Entrance Fees',
            defaults={'item_dk': 'Entrégebyrer', 'display_order': 2}
        )
        self.stdout.write(self.style.SUCCESS('✓ Tour included items created'))

        # Tour Excluded Items
        TourExcluded.objects.get_or_create(
            tour=tour1,
            item='Food and Drinks',
            defaults={'item_dk': 'Mad og drikke', 'display_order': 1}
        )
        TourExcluded.objects.get_or_create(
            tour=tour1,
            item='Hotel Pickup',
            defaults={'item_dk': 'Hotel afhentning', 'display_order': 2}
        )
        self.stdout.write(self.style.SUCCESS('✓ Tour excluded items created'))

        # Tour Itinerary
        TourItinerary.objects.get_or_create(
            tour=tour1,
            step_number=1,
            defaults={
                'title': 'Meeting Point',
                'title_dk': 'Mødested',
                'description': 'Meet at City Hall Square.',
                'description_dk': 'Mød på Rådhuspladsen.',
                'duration_minutes': 15,
                'location': 'City Hall Square'
            }
        )
        TourItinerary.objects.get_or_create(
            tour=tour1,
            step_number=2,
            defaults={
                'title': 'The Little Mermaid',
                'title_dk': 'Den Lille Havfrue',
                'description': 'Visit the famous statue.',
                'description_dk': 'Besøg den berømte statue.',
                'duration_minutes': 30,
                'location': 'Langelinie'
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Tour itinerary created'))

        # Tour Requirements
        TourRequirement.objects.get_or_create(
            tour=tour1,
            requirement='Comfortable walking shoes',
            defaults={
                'requirement_dk': 'Behagelige gadesko',
                'is_mandatory': True,
                'display_order': 1
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Tour requirements created'))

        # Tour FAQs
        TourFAQ.objects.get_or_create(
            tour=tour1,
            question='Is this tour wheelchair accessible?',
            defaults={
                'question_dk': 'Er denne tur kørestolsvenlig?',
                'answer': 'Yes, the route is accessible.',
                'answer_dk': 'Ja, ruten er tilgængelig.',
                'display_order': 1
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Tour FAQs created'))

        # Tour Pricing
        TourPricing.objects.get_or_create(
            tour=tour1,
            participant_type='adult',
            defaults={
                'min_age': 18,
                'max_age': 99,
                'price': Decimal('49.99'),
                'currency': 'DKK',
                'description': 'Adult ticket',
                'description_dk': 'Voksen billet',
                'is_active': True
            }
        )
        TourPricing.objects.get_or_create(
            tour=tour1,
            participant_type='child',
            defaults={
                'min_age': 3,
                'max_age': 17,
                'price': Decimal('29.99'),
                'currency': 'DKK',
                'description': 'Child ticket',
                'description_dk': 'Børnebillet',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Tour pricing created'))

        # Tour Schedule
        TourSchedule.objects.get_or_create(
            tour=tour1,
            date=timezone.now().date() + timedelta(days=1),
            start_time='10:00:00',
            defaults={
                'end_time': '13:00:00',
                'available_slots': 20,
                'booked_slots': 0,
                'status': 'available'
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Tour schedule created'))

        # Tour Blackout Dates
        TourBlackoutDate.objects.get_or_create(
            tour=tour1,
            start_date=timezone.now().date() + timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=31),
            defaults={'reason': 'Public Holiday'}
        )
        self.stdout.write(self.style.SUCCESS('✓ Tour blackout dates created'))

        # Coupons
        coupon1, _ = Coupon.objects.get_or_create(
            code='DEMO20',
            defaults={
                'description': '20% off all tours',
                'discount_type': 'percentage',
                'discount_value': Decimal('20.00'),
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=30),
                'usage_limit': 100,
                'used_count': 5,
                'is_active': True
            }
        )
        coupon2, _ = Coupon.objects.get_or_create(
            code='SAVE10',
            defaults={
                'description': '10% discount coupon',
                'discount_type': 'percentage',
                'discount_value': Decimal('10.00'),
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=60),
                'usage_limit': 50,
                'used_count': 2,
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Coupons created'))

        # Blog Posts
        blog1, _ = BlogPost.objects.get_or_create(
            title='Top 10 Attractions in Copenhagen',
            defaults={
                'title_dk': 'Top 10 Attraktioner i København',
                'author': admin_user,
                'category': culture,
                'content': 'Copenhagen is a beautiful city with many attractions. Here are the top 10 must-see places...',
                'content_dk': 'København er en smuk by med mange attraktioner. Her er de 10 vigtigste seværdigheder...',
                'status': 'published',
                'is_featured': True,
                'published_at': timezone.now() - timedelta(days=5)
            }
        )
        
        blog2, _ = BlogPost.objects.get_or_create(
            title='Viking History in Denmark',
            defaults={
                'title_dk': 'Vikinghistorie i Danmark',
                'author': admin_user,
                'category': culture,
                'content': 'Learn about the fascinating Viking history that shaped Denmark...',
                'content_dk': 'Lær om den fascinerende vikinghistorie, der formede Danmark...',
                'status': 'published',
                'is_featured': False,
                'published_at': timezone.now() - timedelta(days=10)
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Blog posts created'))

        # Customer
        customer, _ = Customer.objects.get_or_create(
            user=demo_user,
            defaults={
                'phone': '+4540123456',
                'address': 'Strøget 10',
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Customer created'))

        # Bookings
        booking1, _ = Booking.objects.get_or_create(
            booking_number='BK001',
            defaults={
                'customer': customer,
                'tour': tour1,
                'tour_date': timezone.now().date() + timedelta(days=7),
                'total_participants': 2,
                'subtotal': Decimal('99.98'),
                'total_amount': Decimal('99.98'),
                'currency': 'DKK',
                'contact_name': demo_user.get_full_name() or demo_user.username,
                'contact_email': demo_user.email,
                'contact_phone': '+4540123456',
                'status': 'confirmed',
                'payment_status': 'paid',
                'special_requirements': 'Please include hotel pickup'
            }
        )
        
        booking2, _ = Booking.objects.get_or_create(
            booking_number='BK002',
            defaults={
                'customer': customer,
                'tour': tour2,
                'tour_date': timezone.now().date() + timedelta(days=14),
                'total_participants': 4,
                'subtotal': Decimal('239.96'),
                'total_amount': Decimal('239.96'),
                'currency': 'DKK',
                'contact_name': demo_user.get_full_name() or demo_user.username,
                'contact_email': demo_user.email,
                'contact_phone': '+4540123456',
                'status': 'confirmed',
                'payment_status': 'pending'
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Bookings created'))

        # Payments
        payment1, _ = Payment.objects.get_or_create(
            transaction_id='TXN123456789',
            defaults={
                'booking': booking1,
                'amount': Decimal('99.98'),
                'currency': 'DKK',
                'payment_method': 'stripe',
                'status': 'completed',
                'paid_at': timezone.now()
            }
        )
        
        payment2, _ = Payment.objects.get_or_create(
            transaction_id='TXN987654321',
            defaults={
                'booking': booking2,
                'amount': Decimal('239.96'),
                'currency': 'DKK',
                'payment_method': 'paypal',
                'status': 'pending',
                'paid_at': None
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Payments created'))

        # Newsletter
        newsletter, _ = Newsletter.objects.get_or_create(
            email='subscriber@yourtourguide.com',
            defaults={
                'name': 'Demo Subscriber',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Newsletter subscription created'))

        # Contact Us
        contact, _ = ContactUs.objects.get_or_create(
            email='contact@example.com',
            defaults={
                'name': 'John Doe',
                'phone': '+4540987654',
                'subject': 'Tour Inquiry',
                'message': 'I would like to inquire about custom group tours.'
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Contact form submission created'))

        # Customer Reviews
        review, _ = CustomerReviewStatic.objects.get_or_create(
            name='Alice Johnson',
            defaults={
                'address': 'Copenhagen, Denmark',
                'review': 'Amazing tours! The guide was very knowledgeable and friendly. Highly recommended!',
                'rating': 5,
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Customer review created'))

        # Sliders
        slider, _ = Slider.objects.get_or_create(
            title='Explore Copenhagen',
            defaults={
                'title_dk': 'Udforsk København',
                'subtitle': 'Discover the beauty of Copenhagen with our guided tours',
                'subtitle_dk': 'Opdag skønheden af København med vores guidede ture',
                'link_url': '/tours/',
                'button_text': 'Explore',
                'display_order': 1,
                'status': 'active'
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Slider created'))

        # Pages
        page, _ = Page.objects.get_or_create(
            slug='about-us',
            defaults={
                'title': 'About Us',
                'title_dk': 'Om Os',
                'content': 'Welcome to Your Tour Guide! We provide the best tours in Denmark...',
                'content_dk': 'Velkommen til Your Tour Guide! Vi leverer de bedste ture i Danmark...',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Page created'))

        self.stdout.write(self.style.SUCCESS('\n✅ All demo data populated successfully!'))
        self.stdout.write(self.style.WARNING('\nDemo credentials:'))
        self.stdout.write(f'Admin User: admin / admin123')
        self.stdout.write(f'Demo User: demouser / demo123')
