from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from accounts.models import (
    Customer, Country, DestinationRegion, SiteSetting, TourSupplier,
    Category, Slider, Newsletter, ContactUs, CustomerReviewStatic,
    Page, City, Tour, TourImage, TourHighlight, TourIncluded, TourExcluded,
    TourItinerary, TourRequirement, TourFAQ, TourPricing, TourSchedule,
    TourTimeSlot, TimeSlot, TourReview, Booking, BookingParticipant,
    Coupon, BlogPost, TeamMember, FeatureSection, FeatureSectionTour,
    WebsiteMenu, WebsiteSubMenu, FAQ, Souvenir, SouvenirOrder,
    SouvenirOrderItem, SouvenirPickuplocation, Bike, BikeAddon,
    BikeAddonPrice, BikeBooking, BikeBookingAddon, Wishlist
)


def get_absolute_url(request, image_field):
    if not image_field:
        return None
    try:
        url = image_field.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url
    except Exception:
        return None


# ==============================================================================
# 1. SITE CONFIG & LAYOUT SERIALIZERS
# ==============================================================================

class SiteSettingSerializer(serializers.ModelSerializer):
    site_logo = serializers.SerializerMethodField()
    site_logo_dark = serializers.SerializerMethodField()
    site_favicon = serializers.SerializerMethodField()

    class Meta:
        model = SiteSetting
        fields = [
            'id', 'site_name', 'site_logo', 'site_logo_dark', 'site_favicon',
            'site_email', 'site_phone', 'site_address', 'site_description',
            'site_metakey', 'site_metadescription', 'site_map',
            'app_google', 'ios_app', 'fb_link', 'x_link', 'insta_link',
            'linkdin_link', 'pintrest_link', 'meetoursuides_description',
            'home_page_title', 'home_page_meta_keywords', 'home_page_meta_description',
            'contactus_page_title', 'contactus_page_meta_keywords', 'contactus_page_meta_description',
            'rentbike_page_title', 'rentbike_page_meta_keywords', 'rentbike_page_meta_description',
            'souvenirs_page_title', 'souvenirs_page_meta_keywords', 'souvenirs_page_meta_description',
            'tours_page_title', 'tours_page_meta_keywords', 'tours_page_meta_description',
            'blog_page_title', 'blog_page_meta_keywords', 'blog_page_meta_description',
            'cvr_number', 'shipping_charge', 'updated_at'
        ]

    def get_site_logo(self, obj):
        return get_absolute_url(self.context.get('request'), obj.site_logo)

    def get_site_logo_dark(self, obj):
        return get_absolute_url(self.context.get('request'), obj.site_logo_dark)

    def get_site_favicon(self, obj):
        return get_absolute_url(self.context.get('request'), obj.site_favicon)


class WebsiteSubMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteSubMenu
        fields = ['id', 'title', 'title_dk', 'status', 'rank', 'link', 'is_open_new_tab']


class WebsiteMenuSerializer(serializers.ModelSerializer):
    submenus = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()

    class Meta:
        model = WebsiteMenu
        fields = [
            'id', 'title', 'title_dk', 'banner', 'is_banner_showing',
            'section_type', 'status', 'rank', 'link', 'is_open_new_tab',
            'has_submenu', 'submenus'
        ]

    def get_banner(self, obj):
        return get_absolute_url(self.context.get('request'), obj.banner)

    def get_submenus(self, obj):
        if not obj.has_submenu:
            return []
        active_submenus = obj.submenus.filter(status='active').order_by('rank')
        return WebsiteSubMenuSerializer(active_submenus, many=True, context=self.context).data


class SliderSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Slider
        fields = [
            'id', 'title', 'title_dk', 'subtitle', 'subtitle_dk',
            'image', 'link_url', 'button_text', 'button_text_dk',
            'display_order', 'status'
        ]

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            'id', 'qus_en', 'qus_dk', 'ans_en', 'ans_dk',
            'is_featured', 'status', 'display_order'
        ]


class CustomerReviewStaticSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    providerimage = serializers.SerializerMethodField()

    class Meta:
        model = CustomerReviewStatic
        fields = [
            'id', 'name', 'address', 'image', 'review', 'review_dk',
            'rating', 'provider', 'otherinfo', 'providerimage',
            'is_active', 'display_order', 'created_at'
        ]

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)

    def get_providerimage(self, obj):
        return get_absolute_url(self.context.get('request'), obj.providerimage)


class PageListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            'id', 'title', 'title_dk', 'slug', 'image',
            'meta_title', 'meta_description', 'display_section', 'is_active'
        ]

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)


class PageDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            'id', 'title', 'title_dk', 'slug', 'image',
            'content', 'content_dk', 'meta_title', 'meta_description',
            'meta_keywords', 'display_section', 'is_active', 'created_at', 'updated_at'
        ]

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)


class TeamMemberSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'image',
            'full_details', 'facebook', 'twitter', 'instagram', 'linkedin', 'pinterest'
        ]

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)


# ==============================================================================
# 2. DESTINATIONS, CATEGORIES & SUPPLIERS
# ==============================================================================

class CountrySerializer(serializers.ModelSerializer):
    flag_image = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    tour_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Country
        fields = [
            'id', 'name', 'code', 'currency_code', 'currency_symbol',
            'timezone', 'language', 'flag_image', 'image', 'is_active', 'tour_count'
        ]

    def get_flag_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.flag_image)

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)


class CitySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_id = serializers.IntegerField(source='country.id', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True, default=None)
    tour_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = City
        fields = [
            'id', 'name', 'name_dk', 'slug', 'description', 'description_dk',
            'image', 'country_id', 'country_name', 'region_id', 'region_name',
            'latitude', 'longitude', 'is_popular', 'is_active', 'tour_count'
        ]

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)


class DestinationRegionSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()
    country_name = serializers.CharField(source='country.name', read_only=True)
    tour_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = DestinationRegion
        fields = [
            'id', 'name', 'name_dk', 'slug', 'description', 'description_dk',
            'image', 'cover_image', 'country_id', 'country_name',
            'latitude', 'longitude', 'is_popular', 'is_active',
            'meta_title', 'meta_description', 'tour_count'
        ]

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)

    def get_cover_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.cover_image)


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    tour_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'name_dk', 'slug', 'description', 'description_dk',
            'image', 'icon', 'parent', 'display_order', 'is_featured', 'status',
            'other_info', 'tour_count'
        ]

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)


class TourSupplierSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    tour_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = TourSupplier
        fields = [
            'id', 'company_name', 'contact_name', 'email', 'phone',
            'address', 'city', 'country', 'website', 'logo',
            'rating', 'total_reviews', 'verified', 'status', 'other_details',
            'tour_count'
        ]

    def get_logo(self, obj):
        return get_absolute_url(self.context.get('request'), obj.logo)


# ==============================================================================
# 3. TOURS & TOUR SUB-RESOURCES
# ==============================================================================

class TourImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = TourImage
        fields = ['id', 'image', 'caption', 'caption_dk', 'display_order', 'is_primary']

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)


class TourHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourHighlight
        fields = ['id', 'highlight', 'highlight_dk', 'icon', 'display_order']


class TourIncludedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourIncluded
        fields = ['id', 'item', 'item_dk', 'display_order']


class TourExcludedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourExcluded
        fields = ['id', 'item', 'item_dk', 'display_order']


class TourItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TourItinerary
        fields = [
            'id', 'step_number', 'title', 'title_dk', 'description', 'description_dk',
            'duration_minutes', 'location', 'latitude', 'longitude'
        ]


class TourRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourRequirement
        fields = ['id', 'requirement', 'requirement_dk', 'is_mandatory', 'display_order']


class TourFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourFAQ
        fields = ['id', 'question', 'question_dk', 'answer', 'answer_dk', 'display_order']


class TourPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPricing
        fields = [
            'id', 'participant_type', 'min_age', 'max_age',
            'price', 'currency', 'description', 'description_dk', 'is_active'
        ]


class TourScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourSchedule
        fields = [
            'id', 'date', 'start_time', 'end_time', 'available_slots',
            'booked_slots', 'price_override', 'status', 'notes'
        ]


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'name', 'status']


class TourReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_image = serializers.SerializerMethodField()

    class Meta:
        model = TourReview
        fields = [
            'id', 'customer_name', 'customer_image', 'overall_rating',
            'value_rating', 'service_rating', 'organization_rating',
            'title', 'review', 'verified_booking', 'helpful_count',
            'supplier_response', 'supplier_response_date', 'created_at'
        ]

    def get_customer_name(self, obj):
        if obj.customer and obj.customer.user:
            name = f"{obj.customer.user.first_name} {obj.customer.user.last_name}".strip()
            return name if name else obj.customer.user.username
        return "Anonymous"

    def get_customer_image(self, obj):
        if obj.customer and obj.customer.profile_image:
            return get_absolute_url(self.context.get('request'), obj.customer.profile_image)
        return None


class TourReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourReview
        fields = [
            'overall_rating', 'value_rating', 'service_rating',
            'organization_rating', 'title', 'review'
        ]


class TourListSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    destination_region = DestinationRegionSerializer(read_only=True)
    supplier = TourSupplierSerializer(read_only=True)
    calculated_average_rating = serializers.FloatField(read_only=True, default=0.0)
    calculated_total_reviews = serializers.IntegerField(read_only=True, default=0)
    slug_id = serializers.CharField(read_only=True)
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Tour
        fields = [
            'id', 'title', 'title_dk', 'slug', 'slug_id', 'short_description', 'short_description_dk',
            'main_image', 'duration_hours', 'duration_text', 'min_participants', 'max_participants',
            'age_restriction', 'difficulty_level', 'base_price', 'original_price', 'before_discount_price',
            'before_discount_price_statue', 'before_discount_price_text', 'currency', 'discount_percentage',
            'meeting_point', 'meeting_point_dk', 'meeting_point_latitude', 'meeting_point_longitude',
            'instant_confirmation', 'free_cancellation', 'cancellation_hours', 'mobile_ticket',
            'skip_the_line', 'live_guide', 'audio_guide', 'wheelchair_accessible', 'languages_offered',
            'calculated_average_rating', 'calculated_total_reviews', 'is_featured', 'is_bestseller',
            'status', 'rank', 'category', 'city', 'destination_region', 'supplier'
        ]

    def get_main_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.main_image)


class TourDetailSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    images = TourImageSerializer(many=True, read_only=True)
    highlights = TourHighlightSerializer(many=True, read_only=True)
    included_items = TourIncludedSerializer(many=True, read_only=True)
    excluded_items = TourExcludedSerializer(many=True, read_only=True)
    itinerary_steps = TourItinerarySerializer(many=True, read_only=True)
    requirements = TourRequirementSerializer(many=True, read_only=True)
    faqs = TourFAQSerializer(many=True, read_only=True)
    pricing_options = serializers.SerializerMethodField()
    time_slots = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    destination_region = DestinationRegionSerializer(read_only=True)
    supplier = TourSupplierSerializer(read_only=True)
    calculated_average_rating = serializers.FloatField(read_only=True, default=0.0)
    calculated_total_reviews = serializers.IntegerField(read_only=True, default=0)
    slug_id = serializers.CharField(read_only=True)
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    reviews = serializers.SerializerMethodField()
    related_tours = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            'id', 'title', 'title_dk', 'slug', 'slug_id', 'short_description', 'short_description_dk',
            'description', 'description_dk', 'main_image', 'images', 'video_url',
            'duration_hours', 'duration_text', 'min_participants', 'max_participants',
            'age_restriction', 'difficulty_level', 'base_price', 'original_price',
            'before_discount_price', 'before_discount_price_statue', 'before_discount_price_text',
            'currency', 'discount_percentage', 'meeting_point', 'meeting_point_dk',
            'meeting_point_latitude', 'meeting_point_longitude', 'map_location', 'available_days',
            'start_date', 'end_date', 'instant_confirmation', 'free_cancellation',
            'cancellation_hours', 'mobile_ticket', 'skip_the_line', 'live_guide', 'audio_guide',
            'wheelchair_accessible', 'languages_offered', 'calculated_average_rating',
            'calculated_total_reviews', 'meta_title', 'meta_description', 'meta_keywords',
            'is_featured', 'is_bestseller', 'status', 'rank',
            'category', 'city', 'destination_region', 'supplier',
            'highlights', 'included_items', 'excluded_items', 'itinerary_steps',
            'requirements', 'faqs', 'pricing_options', 'time_slots', 'reviews', 'related_tours'
        ]

    def get_main_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.main_image)

    def get_pricing_options(self, obj):
        active_options = obj.pricing_options.filter(is_active=True).order_by('price')
        return TourPricingSerializer(active_options, many=True, context=self.context).data

    def get_time_slots(self, obj):
        slots = [ts.time_slot for ts in obj.tour_timeslots.select_related('time_slot').all() if ts.time_slot]
        return TimeSlotSerializer(slots, many=True).data

    def get_reviews(self, obj):
        approved_reviews = obj.reviews.filter(status='approved').order_by('-created_at')[:10]
        return TourReviewSerializer(approved_reviews, many=True, context=self.context).data

    def get_related_tours(self, obj):
        related = Tour.objects.filter(status='active').exclude(pk=obj.pk)
        if obj.category:
            related = related.filter(category=obj.category)
        elif obj.destination_region:
            related = related.filter(destination_region=obj.destination_region)
        return TourListSerializer(related.select_related('supplier', 'category', 'city', 'destination_region')[:4], many=True, context=self.context).data


class FeatureSectionSerializer(serializers.ModelSerializer):
    banner = serializers.SerializerMethodField()
    tours = serializers.SerializerMethodField()

    class Meta:
        model = FeatureSection
        fields = [
            'id', 'title', 'title_dk', 'banner', 'is_banner_showing',
            'short_description', 'short_description_dk', 'description', 'description_dk',
            'status', 'rank', 'tours'
        ]

    def get_banner(self, obj):
        return get_absolute_url(self.context.get('request'), obj.banner)

    def get_tours(self, obj):
        active_tours = [
            fst.tour for fst in obj.section_tours.select_related('tour__supplier', 'tour__category', 'tour__city', 'tour__destination_region').all()
            if fst.tour and fst.tour.status == 'active'
        ]
        return TourListSerializer(active_tours, many=True, context=self.context).data


# ==============================================================================
# 4. COUPONS, BOOKINGS & PARTICIPANTS
# ==============================================================================

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'description_dk', 'discount_type',
            'discount_value', 'max_discount_amount', 'valid_from', 'valid_until',
            'min_purchase_amount'
        ]


class BookingParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingParticipant
        fields = [
            'id', 'participant_type', 'first_name', 'last_name',
            'age', 'email', 'phone', 'special_requirements', 'price'
        ]


class BookingSerializer(serializers.ModelSerializer):
    participants = BookingParticipantSerializer(many=True, read_only=True)
    tour_title = serializers.CharField(source='tour.title', read_only=True)
    tour_slug = serializers.CharField(source='tour.slug', read_only=True)
    tour_image = serializers.SerializerMethodField()
    meeting_point = serializers.CharField(source='tour.meeting_point', read_only=True)
    tour_time_slot = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_number', 'tour_id', 'tour_title', 'tour_slug', 'tour_image',
            'meeting_point', 'booking_date', 'tour_date', 'tour_time', 'tour_time_slot',
            'total_participants', 'subtotal', 'discount_amount', 'tax_amount', 'total_amount',
            'currency', 'contact_name', 'contact_email', 'contact_phone',
            'special_requirements', 'pickup_location', 'country', 'status',
            'payment_status', 'participants', 'created_at'
        ]

    def get_tour_image(self, obj):
        if obj.tour and obj.tour.main_image:
            return get_absolute_url(self.context.get('request'), obj.tour.main_image)
        return None

    def get_tour_time_slot(self, obj):
        if obj.tour_time_slot and obj.tour_time_slot.time_slot:
            return obj.tour_time_slot.time_slot.name
        return None


class BookingCreateSerializer(serializers.Serializer):
    tour_id = serializers.IntegerField(required=True)
    tour_date = serializers.DateField(required=True)
    tour_time = serializers.CharField(required=False, allow_blank=True, default='')
    tour_time_slot = serializers.CharField(required=False, allow_blank=True, default='')
    schedule_id = serializers.IntegerField(required=False, allow_null=True)
    contact_name = serializers.CharField(required=True, max_length=255)
    contact_email = serializers.EmailField(required=True)
    contact_phone = serializers.CharField(required=False, allow_blank=True, max_length=50)
    country = serializers.CharField(required=False, allow_blank=True, max_length=100)
    special_requirements = serializers.CharField(required=False, allow_blank=True)
    pickup_location = serializers.CharField(required=False, allow_blank=True)
    customer_notes = serializers.CharField(required=False, allow_blank=True)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    participants = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        allow_empty=False
    )


# ==============================================================================
# 5. BLOG SERIALIZERS
# ==============================================================================

class BlogPostListSerializer(serializers.ModelSerializer):
    featured_image = serializers.SerializerMethodField()
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'title_dk', 'slug', 'featured_image', 'excerpt', 'excerpt_dk',
            'author_name', 'category_name', 'view_count', 'is_featured', 'published_at', 'created_at'
        ]

    def get_featured_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.featured_image)


class BlogPostDetailSerializer(serializers.ModelSerializer):
    featured_image = serializers.SerializerMethodField()
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    related_posts = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'title_dk', 'slug', 'featured_image', 'excerpt', 'excerpt_dk',
            'content', 'content_dk', 'author_name', 'category_name', 'view_count',
            'meta_title', 'meta_description', 'meta_keywords', 'is_featured',
            'published_at', 'created_at', 'updated_at', 'related_posts'
        ]

    def get_featured_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.featured_image)

    def get_related_posts(self, obj):
        related = BlogPost.objects.filter(status='published').exclude(pk=obj.pk)
        if obj.category:
            related = related.filter(category=obj.category)
        return BlogPostListSerializer(related[:3], many=True, context=self.context).data


# ==============================================================================
# 6. SOUVENIRS & CART SERIALIZERS
# ==============================================================================

class SouvenirSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    slug_id = serializers.CharField(read_only=True)

    class Meta:
        model = Souvenir
        fields = [
            'id', 'title', 'title_dk', 'slug_id', 'image', 'description', 'description_dk',
            'price', 'before_discount_price', 'before_discount_price_statue',
            'before_discount_price_text', 'status', 'stock', 'created_at'
        ]

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)


class SouvenirPickuplocationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = SouvenirPickuplocation
        fields = [
            'id', 'name', 'contact_person_name', 'email', 'phone',
            'address', 'other_info', 'image', 'status'
        ]

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)


class SouvenirOrderItemSerializer(serializers.ModelSerializer):
    souvenir_title = serializers.CharField(source='souvenir.title', read_only=True)
    souvenir_image = serializers.SerializerMethodField()

    class Meta:
        model = SouvenirOrderItem
        fields = ['id', 'souvenir_id', 'souvenir_title', 'souvenir_image', 'price', 'quantity']

    def get_souvenir_image(self, obj):
        if obj.souvenir and obj.souvenir.image:
            return get_absolute_url(self.context.get('request'), obj.souvenir.image)
        return None


class SouvenirOrderSerializer(serializers.ModelSerializer):
    items = SouvenirOrderItemSerializer(many=True, read_only=True)
    pickup_location_name = serializers.CharField(source='pickup_location.name', read_only=True, default=None)

    class Meta:
        model = SouvenirOrder
        fields = [
            'id', 'order_number', 'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'postal_code', 'delivery_method',
            'pickup_location_id', 'pickup_location_name', 'pickup_date', 'pickup_time',
            'shipping_charge', 'total_amount', 'status', 'items', 'created_at'
        ]


class SouvenirOrderCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True, max_length=30)
    delivery_method = serializers.ChoiceField(choices=['delivery', 'pickup'], default='delivery')
    address = serializers.CharField(required=False, allow_blank=True, default='')
    city = serializers.CharField(required=False, allow_blank=True, default='')
    postal_code = serializers.CharField(required=False, allow_blank=True, default='')
    pickup_location_id = serializers.IntegerField(required=False, allow_null=True)
    pickup_date = serializers.DateField(required=False, allow_null=True)
    pickup_time = serializers.TimeField(required=False, allow_null=True)
    items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Optional items list if not relying on session cart: [{'souvenir_id': 1, 'quantity': 2}]"
    )


# ==============================================================================
# 7. BIKE RENTAL SERIALIZERS
# ==============================================================================

class BikeAddonSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = BikeAddon
        fields = ['id', 'title', 'title_dk', 'image', 'description', 'description_dk', 'status']

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)


class BikeAddonPriceSerializer(serializers.ModelSerializer):
    addon = BikeAddonSerializer(read_only=True)

    class Meta:
        model = BikeAddonPrice
        fields = ['id', 'addon', 'price']


class BikeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    addons = serializers.SerializerMethodField()

    class Meta:
        model = Bike
        fields = [
            'id', 'title', 'title_dk', 'slug', 'image', 'shortdescription',
            'shortdescription_dk', 'description', 'description_dk',
            'price', 'show_discount', 'price_before_disount', 'height_info',
            'width_info', 'gear_info', 'is_unisex', 'is_helmet_recommended',
            'is_electric', 'top_speed_info', 'rank', 'pickup_location',
            'pickup_location_latitude', 'pickup_location_longitude', 'addons'
        ]

    def get_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.image)

    def get_addons(self, obj):
        addons_pricing = obj.bike_addons.select_related('addon').filter(addon__status='active')
        return BikeAddonPriceSerializer(addons_pricing, many=True, context=self.context).data


class BikeBookingAddonSerializer(serializers.ModelSerializer):
    addon_title = serializers.CharField(source='addon.title', read_only=True)

    class Meta:
        model = BikeBookingAddon
        fields = ['id', 'addon_id', 'addon_title', 'price', 'quantity']


class BikeBookingSerializer(serializers.ModelSerializer):
    addons = BikeBookingAddonSerializer(source='booking_addons', many=True, read_only=True)
    bike_title = serializers.CharField(source='bike.title', read_only=True)
    bike_image = serializers.SerializerMethodField()

    class Meta:
        model = BikeBooking
        fields = [
            'id', 'booking_number', 'bike_id', 'bike_title', 'bike_image',
            'bike_quantity', 'start_date', 'end_date', 'start_time', 'end_time',
            'name', 'email', 'phone', 'address', 'other_info',
            'subtotal', 'discount', 'total', 'paid', 'status',
            'number_of_days', 'addons', 'created_at'
        ]

    def get_bike_image(self, obj):
        if obj.bike and obj.bike.image:
            return get_absolute_url(self.context.get('request'), obj.bike.image)
        return None


class BikeBookingCreateSerializer(serializers.Serializer):
    bike_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True, max_length=50)
    address = serializers.CharField(required=False, allow_blank=True, default='')
    other_info = serializers.CharField(required=False, allow_blank=True, default='')
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    start_time = serializers.CharField(required=False, allow_blank=True, default='')
    end_time = serializers.CharField(required=False, allow_blank=True, default='')
    bike_quantity = serializers.IntegerField(required=False, default=1, min_value=1)
    addons = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
        help_text="List of addon selections: [{'addon_id': 1, 'quantity': 2}]"
    )


# ==============================================================================
# 8. CONTACT & NEWSLETTER
# ==============================================================================

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message']


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ['id', 'email', 'name']


# ==============================================================================
# 9. CUSTOMER AUTHENTICATION & PROFILE
# ==============================================================================

class CustomerProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'phone', 'address', 'date_of_birth',
            'nationality', 'profile_image', 'preferred_language'
        ]

    def get_profile_image(self, obj):
        return get_absolute_url(self.context.get('request'), obj.profile_image)


class CustomerUserSerializer(serializers.ModelSerializer):
    profile = CustomerProfileSerializer(source='customer_profile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class CustomerRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150, default='')
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, min_length=6, write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()


class CustomerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class CustomerProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    preferred_language = serializers.CharField(required=False, allow_blank=True)


class WishlistSerializer(serializers.ModelSerializer):
    tour = TourListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'tour', 'created_at']
