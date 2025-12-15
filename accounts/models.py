from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='customers/', blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default='en', choices=[('en', 'English'), ('dk', 'Danish')])
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.user.username

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=5, blank=True, help_text='ISO country code', default='')
    currency_code = models.CharField(max_length=3, blank=True, help_text='ISO currency code (e.g., DKK, USD)', default='')
    currency_symbol = models.CharField(max_length=10, blank=True, default='')
    timezone = models.CharField(max_length=50, blank=True, default='')
    language = models.CharField(max_length=10, blank=True, default='')
    flag_image = models.ImageField(upload_to='countries/', blank=True, null=True)
    image = models.ImageField(upload_to='countries/destinations/', blank=True, null=True, help_text='Main destination image for the country')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']

    def __str__(self):
        return self.name

class DestinationRegion(models.Model):
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='regions')
    name = models.CharField(max_length=200)
    name_dk = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    description_dk = models.TextField(blank=True)
    image = models.ImageField(upload_to='regions/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='regions/covers/', blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Destination Region"
        verbose_name_plural = "Destination Regions"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class SiteSetting(models.Model):
    site_name = models.CharField(max_length=200, default='Your Tour Guide')
    site_logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    site_favicon = models.ImageField(upload_to='settings/', blank=True, null=True)
    site_email = models.EmailField(blank=True)
    site_address = models.TextField(blank=True)
    site_description = models.TextField(blank=True)
    site_metakey = models.TextField(blank=True, help_text='Comma-separated keywords')
    site_metadescription = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    site_phone = models.TextField(blank=True)

    site_map = models.TextField(blank=True)
    app_google = models.CharField(blank=True)
    ios_app = models.CharField(blank=True)
    fb_link = models.CharField(blank=True)
    x_link = models.CharField(blank=True)
    insta_link = models.CharField(blank=True)
    linkdin_link = models.CharField(blank=True)
    pintrest_link = models.CharField(blank=True)
    site_logo_dark = models.ImageField(upload_to='settings/', blank=True, null=True)

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteSetting.objects.exists():
            raise ValueError('Only one SiteSetting instance is allowed')
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the single settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

class TourSupplier(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    )

    company_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200, verbose_name='Contact Person Name', default='')
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='suppliers')
    website = models.URLField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='suppliers/', blank=True, null=True)
    tax_id = models.CharField(max_length=100, blank=True)
    payment_details = models.TextField(blank=True)
    bank_account = models.CharField(max_length=100, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Commission percentage',blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    other_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Tour Supplier"
        verbose_name_plural = "Tour Suppliers"

    def __str__(self):
        return self.company_name

class Category(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    name = models.CharField(max_length=200)
    name_dk = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True)
    description_dk = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, help_text='Icon class or SVG')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    display_order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    other_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Slider(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    title = models.CharField(max_length=200, blank=True, null=True)
    title_dk = models.CharField(max_length=200, blank=True, null=True)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    subtitle_dk = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='sliders/', blank=True, null=True)
    link_url = models.URLField(max_length=500, blank=True)
    button_text = models.CharField(max_length=100, blank=True)
    button_text_dk = models.CharField(max_length=100, blank=True)
    display_order = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Sliders"
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title if self.title else f"Slider #{self.id}"

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Newsletters"
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class ContactUs(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, default='')
    subject = models.CharField(max_length=200, blank=True, default='')
    message = models.TextField()
    is_notified = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    reply_message = models.TextField(blank=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"

class CustomerReviewStatic(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    image = models.ImageField(upload_to='reviews/', blank=True, null=True)
    review = models.TextField()
    review_dk = models.TextField(blank=True)
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Review"
        verbose_name_plural = "Customer Reviews"
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating} stars"

class Page(models.Model):
    title = models.CharField(max_length=200)
    title_dk = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    image = models.ImageField(upload_to='pages/', blank=True, null=True)
    content = models.TextField(blank=True)
    content_dk = models.TextField(blank=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    display_section = models.CharField(max_length=20, choices=[
        ('header', 'Header'),
        ('footer', 'Footer'),
        ('default', 'Default')
    ], default='default')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class City(models.Model):
    region = models.ForeignKey(DestinationRegion, on_delete=models.SET_NULL, null=True, related_name='cities')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=200)
    name_dk = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True)
    description_dk = models.TextField(blank=True)
    image = models.ImageField(upload_to='cities/', blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Tour(models.Model):
    supplier = models.ForeignKey(TourSupplier, on_delete=models.CASCADE, related_name='tours')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='tours')
    destination_region = models.ForeignKey(DestinationRegion, on_delete=models.SET_NULL, null=True, related_name='tours')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='tours')
    
    title = models.CharField(max_length=300)
    title_dk = models.CharField(max_length=300, blank=True)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    short_description = models.TextField(blank=True)
    short_description_dk = models.TextField(blank=True)
    description = models.TextField()
    description_dk = models.TextField(blank=True)
    
    main_image = models.ImageField(upload_to='tours/', blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True)
    
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    duration_text = models.CharField(max_length=100, blank=True)
    min_participants = models.IntegerField(default=1)
    max_participants = models.IntegerField(blank=True, null=True)
    age_restriction = models.CharField(max_length=100, blank=True)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
        ('extreme', 'Extreme')
    ], default='easy')
    
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='DKK')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    meeting_point = models.TextField(blank=True)
    meeting_point_dk = models.TextField(blank=True)
    meeting_point_latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    meeting_point_longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    map_location = models.TextField(blank=True, help_text="Enter the Google Maps Embed URL")
    
    available_days = models.JSONField(default=list, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    instant_confirmation = models.BooleanField(default=False)
    free_cancellation = models.BooleanField(default=False)
    cancellation_hours = models.IntegerField(default=24)
    mobile_ticket = models.BooleanField(default=True)
    skip_the_line = models.BooleanField(default=False)
    live_guide = models.BooleanField(default=True)
    audio_guide = models.BooleanField(default=False)
    wheelchair_accessible = models.BooleanField(default=False)
    
    languages_offered = models.JSONField(default=list, blank=True)
    
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    total_bookings = models.IntegerField(default=0)
    
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived')
    ], default='draft')
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def original_price(self):
        """Calculate the original price before discount"""
        if self.discount_percentage > 0:
            return self.base_price / (1 - self.discount_percentage / 100)
        return self.base_price

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class TourImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tours/gallery/')
    caption = models.CharField(max_length=300, blank=True)
    caption_dk = models.CharField(max_length=300, blank=True)
    display_order = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']

class TourHighlight(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='highlights')
    highlight = models.TextField()
    highlight_dk = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']

class TourIncluded(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='included_items')
    item = models.TextField()
    item_dk = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']

class TourExcluded(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='excluded_items')
    item = models.TextField()
    item_dk = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']

class TourItinerary(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='itinerary_steps')
    step_number = models.IntegerField()
    title = models.CharField(max_length=300)
    title_dk = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    description_dk = models.TextField(blank=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['step_number']

class TourRequirement(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='requirements')
    requirement = models.TextField()
    requirement_dk = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']

class TourFAQ(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='faqs')
    question = models.TextField()
    question_dk = models.TextField(blank=True)
    answer = models.TextField()
    answer_dk = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']

class TourPricing(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='pricing_options')
    participant_type = models.CharField(max_length=50, choices=[
        ('adult', 'Adult'),
        ('child', 'Child'),
        ('infant', 'Infant'),
        ('senior', 'Senior'),
        ('student', 'Student'),
        ('group', 'Group')
    ])
    min_age = models.IntegerField(blank=True, null=True)
    max_age = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='DKK')
    description = models.CharField(max_length=200, blank=True)
    description_dk = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TourSchedule(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    available_slots = models.IntegerField()
    booked_slots = models.IntegerField(default=0)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('available', 'Available'),
        ('full', 'Full'),
        ('cancelled', 'Cancelled')
    ], default='available')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['tour', 'date', 'start_time']

class TourBlackoutDate(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='blackout_dates')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Booking(models.Model):
    booking_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='bookings')
    schedule = models.ForeignKey(TourSchedule, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    booking_date = models.DateTimeField(auto_now_add=True)
    tour_date = models.DateField()
    tour_time = models.TimeField(blank=True, null=True)
    
    total_participants = models.IntegerField()
    participant_details = models.JSONField(default=dict, blank=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='DKK')
    
    contact_name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=50)
    
    special_requirements = models.TextField(blank=True)
    pickup_location = models.CharField(max_length=300, blank=True)
    
    status = models.CharField(max_length=30, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('no_show', 'No Show')
    ], default='pending')
    
    payment_status = models.CharField(max_length=30, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed')
    ], default='pending')
    
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    confirmed_at = models.DateTimeField(blank=True, null=True)
    confirmation_code = models.CharField(max_length=50, blank=True)
    
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class BookingParticipant(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='participants')
    participant_type = models.CharField(max_length=50)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    age = models.IntegerField(blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    special_requirements = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('bank_transfer', 'Bank Transfer')
    ])
    payment_gateway = models.CharField(max_length=50, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='DKK')
    
    status = models.CharField(max_length=30, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=50, blank=True)
    
    gateway_response = models.JSONField(default=dict, blank=True)
    
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    refund_reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
    
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TourReview(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='review')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews')
    
    overall_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    value_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    service_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    organization_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    
    title = models.CharField(max_length=300, blank=True)
    review = models.TextField()
    
    images = models.JSONField(default=list, blank=True)
    
    verified_booking = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged')
    ], default='pending')
    is_featured = models.BooleanField(default=False)
    
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    
    supplier_response = models.TextField(blank=True)
    supplier_response_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class ReviewHelpful(models.Model):
    review = models.ForeignKey(TourReview, on_delete=models.CASCADE, related_name='helpful_votes')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='helpful_votes')
    is_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'customer']

class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='wishlist')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'tour']

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=300, blank=True)
    description_dk = models.CharField(max_length=300, blank=True)
    
    discount_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount')
    ])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    usage_limit = models.IntegerField(blank=True, null=True)
    usage_per_customer = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)
    
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    applicable_tours = models.JSONField(default=list, blank=True)
    applicable_categories = models.JSONField(default=list, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='coupon_usages')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='coupon_usages')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=300)
    message = models.TextField()
    
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_posts')
    
    title = models.CharField(max_length=300)
    title_dk = models.CharField(max_length=300, blank=True)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    excerpt = models.TextField(blank=True)
    excerpt_dk = models.TextField(blank=True)
    content = models.TextField()
    content_dk = models.TextField(blank=True)
    
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    
    view_count = models.IntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], default='draft')
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class TourView(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='views')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(max_length=500, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

class SearchLog(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    search_query = models.CharField(max_length=500)
    filters = models.JSONField(default=dict, blank=True)
    results_count = models.IntegerField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    searched_at = models.DateTimeField(auto_now_add=True)

class CustomerMessage(models.Model):
    SENDER_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=20, choices=SENDER_CHOICES)
    sender_admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_messages')
    subject = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer Message'
        verbose_name_plural = 'Customer Messages'
    
    def __str__(self):
        return f"{self.customer.user.username} - {self.subject}"
    
    def get_thread_messages(self):
        """Get all messages in this conversation thread"""
        if self.parent_message:
            return self.parent_message.get_thread_messages()
        # Get all messages in this thread
        return CustomerMessage.objects.filter(parent_message=self).order_by('created_at')

class FeatureSection(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    title = models.CharField(max_length=200)
    title_dk = models.CharField(max_length=200, blank=True)
    banner = models.ImageField(upload_to='feature_sections/', blank=True, null=True)
    is_banner_showing = models.BooleanField(default=True)
    short_description = models.TextField(blank=True)
    short_description_dk = models.TextField(blank=True)
    description = models.TextField(blank=True)
    description_dk = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    rank = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rank', '-created_at']
        verbose_name = "Feature Section"
        verbose_name_plural = "Feature Sections"

    def __str__(self):
        return self.title

class FeatureSectionTour(models.Model):
    feature_section = models.ForeignKey(FeatureSection, on_delete=models.CASCADE, related_name='section_tours')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Feature Section Tour"
        verbose_name_plural = "Feature Section Tours"
        unique_together = ('feature_section', 'tour')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.feature_section.title} - {self.tour.title}"

class WebsiteMenu(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    
    SECTION_TYPE_CHOICES = (
        ('header', 'Header'),
        ('footer', 'Footer'),
    )

    title = models.CharField(max_length=200)
    title_dk = models.CharField(max_length=200, blank=True)
    banner = models.ImageField(upload_to='website_menus/', blank=True, null=True)
    is_banner_showing = models.BooleanField(default=True)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPE_CHOICES, default='header')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    rank = models.IntegerField(default=0)
    link = models.CharField(max_length=500, blank=True)
    is_open_new_tab = models.BooleanField(default=False)
    has_submenu = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rank', '-created_at']
        verbose_name = "Website Menu"
        verbose_name_plural = "Website Menus"

    def __str__(self):
        return self.title

class WebsiteSubMenu(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    menu = models.ForeignKey(WebsiteMenu, on_delete=models.CASCADE, related_name='submenus')
    title = models.CharField(max_length=200)
    title_dk = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    rank = models.IntegerField(default=0)
    link = models.CharField(max_length=500, blank=True)
    is_open_new_tab = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rank', '-created_at']
        verbose_name = "Website SubMenu"
        verbose_name_plural = "Website SubMenus"

    def __str__(self):
        return f"{self.menu.title} - {self.title}"

class FAQ(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    qus_en = models.TextField(verbose_name='Question (English)')
    qus_dk = models.TextField(verbose_name='Question (Danish)', blank=True)
    ans_en = models.TextField(verbose_name='Answer (English)')
    ans_dk = models.TextField(verbose_name='Answer (Danish)', blank=True)
    is_featured = models.BooleanField(default=False, verbose_name='Featured')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    display_order = models.IntegerField(default=0, verbose_name='Display Order')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.qus_en[:50]
