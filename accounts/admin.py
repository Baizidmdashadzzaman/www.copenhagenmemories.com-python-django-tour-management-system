from django.contrib import admin
from .models import (
    Customer, Country, DestinationRegion, City, SiteSetting, TourSupplier, Category, Slider,
    Newsletter, ContactUs, CustomerReviewStatic, Page, Tour, TourImage, TourHighlight,
    TourIncluded, TourExcluded, TourItinerary, TourRequirement, TourFAQ, TourPricing,
    TourSchedule, TourBlackoutDate, Booking, BookingParticipant, Payment, TourReview,
    ReviewHelpful, Wishlist, Coupon, CouponUsage, Notification, BlogPost, TourView, SearchLog,
    CustomerMessage, FeatureSection, FeatureSectionTour, WebsiteMenu, WebsiteSubMenu, FAQ
)


# Register your models here.
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    search_fields = ('name', 'code')

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_email', 'updated_at')
    
    def has_add_permission(self, request):
        # Check if an instance already exists
        if SiteSetting.objects.exists():
            return False
        return True

@admin.register(DestinationRegion)
class DestinationRegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'is_active', 'created_at')
    list_filter = ('is_active', 'country')
    search_fields = ('name', 'description')

@admin.register(TourSupplier)
class TourSupplierAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_name', 'email', 'phone', 'verified', 'status', 'created_at')
    list_filter = ('verified', 'status', 'created_at')
    search_fields = ('company_name', 'contact_name', 'email', 'phone')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_dk', 'slug', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'name_dk', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'title_dk', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'title_dk', 'subtitle', 'subtitle_dk')

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)

@admin.register(CustomerReviewStatic)
class CustomerReviewStaticAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'rating', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'rating', 'created_at')
    search_fields = ('name', 'address', 'review', 'review_dk')

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'title_dk', 'content', 'content_dk')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'phone', 'nationality', 'preferred_language', 'created_at')
    list_filter = ('preferred_language', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'address')
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'country', 'is_popular', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_popular', 'country', 'created_at')
    search_fields = ('name', 'name_dk', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_notified', 'is_replied', 'created_at')
    list_filter = ('is_notified', 'is_replied', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'supplier', 'category', 'status', 'base_price', 'average_rating', 'is_featured', 'created_at')
    list_filter = ('status', 'is_featured', 'is_bestseller', 'difficulty_level', 'created_at')
    search_fields = ('title', 'title_dk', 'description', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {'fields': ('title', 'title_dk', 'slug', 'supplier', 'category', 'destination_region', 'city')}),
        ('Description', {'fields': ('short_description', 'short_description_dk', 'description', 'description_dk')}),
        ('Media', {'fields': ('main_image', 'video_url')}),
        ('Tour Details', {'fields': ('duration_hours', 'duration_text', 'min_participants', 'max_participants', 'age_restriction', 'difficulty_level')}),
        ('Pricing', {'fields': ('base_price', 'currency', 'discount_percentage')}),
        ('Location', {'fields': ('meeting_point', 'meeting_point_dk', 'meeting_point_latitude', 'meeting_point_longitude', 'map_location')}),
        ('Availability', {'fields': ('available_days', 'start_date', 'end_date')}),
        ('Features', {'fields': ('instant_confirmation', 'free_cancellation', 'cancellation_hours', 'mobile_ticket', 'skip_the_line', 'live_guide', 'audio_guide', 'wheelchair_accessible')}),
        ('Languages & Ratings', {'fields': ('languages_offered', 'average_rating', 'total_reviews', 'total_bookings')}),
        ('SEO', {'fields': ('meta_title', 'meta_description', 'meta_keywords')}),
        ('Status', {'fields': ('status', 'is_featured', 'is_bestseller', 'created_at', 'updated_at')}),
    )

@admin.register(TourImage)
class TourImageAdmin(admin.ModelAdmin):
    list_display = ('tour', 'caption', 'display_order', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('tour__title', 'caption', 'caption_dk')

@admin.register(TourHighlight)
class TourHighlightAdmin(admin.ModelAdmin):
    list_display = ('tour', 'icon', 'display_order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('tour__title', 'highlight', 'highlight_dk')

@admin.register(TourIncluded)
class TourIncludedAdmin(admin.ModelAdmin):
    list_display = ('tour', 'display_order', 'created_at')
    search_fields = ('tour__title', 'item', 'item_dk')

@admin.register(TourExcluded)
class TourExcludedAdmin(admin.ModelAdmin):
    list_display = ('tour', 'display_order', 'created_at')
    search_fields = ('tour__title', 'item', 'item_dk')

@admin.register(TourItinerary)
class TourItineraryAdmin(admin.ModelAdmin):
    list_display = ('tour', 'step_number', 'title', 'duration_minutes', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('tour__title', 'title', 'title_dk', 'location')

@admin.register(TourRequirement)
class TourRequirementAdmin(admin.ModelAdmin):
    list_display = ('tour', 'is_mandatory', 'display_order', 'created_at')
    list_filter = ('is_mandatory', 'created_at')
    search_fields = ('tour__title', 'requirement', 'requirement_dk')

@admin.register(TourFAQ)
class TourFAQAdmin(admin.ModelAdmin):
    list_display = ('tour', 'question', 'display_order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('tour__title', 'question', 'question_dk', 'answer')

@admin.register(TourPricing)
class TourPricingAdmin(admin.ModelAdmin):
    list_display = ('tour', 'participant_type', 'price', 'currency', 'is_active', 'created_at')
    list_filter = ('participant_type', 'is_active', 'created_at')
    search_fields = ('tour__title', 'description')

@admin.register(TourSchedule)
class TourScheduleAdmin(admin.ModelAdmin):
    list_display = ('tour', 'date', 'start_time', 'available_slots', 'booked_slots', 'status', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('tour__title', 'notes')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TourBlackoutDate)
class TourBlackoutDateAdmin(admin.ModelAdmin):
    list_display = ('tour', 'start_date', 'end_date', 'reason', 'created_at')
    list_filter = ('start_date', 'created_at')
    search_fields = ('tour__title', 'reason')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_number', 'customer', 'tour', 'tour_date', 'status', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status', 'tour_date', 'created_at')
    search_fields = ('booking_number', 'customer__user__username', 'contact_email', 'tour__title')
    readonly_fields = ('booking_number', 'created_at', 'updated_at')

@admin.register(BookingParticipant)
class BookingParticipantAdmin(admin.ModelAdmin):
    list_display = ('booking', 'first_name', 'last_name', 'participant_type', 'price', 'created_at')
    list_filter = ('participant_type', 'created_at')
    search_fields = ('booking__booking_number', 'first_name', 'last_name', 'email')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'transaction_id', 'payment_method', 'amount', 'status', 'paid_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('booking__booking_number', 'transaction_id', 'card_brand')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TourReview)
class TourReviewAdmin(admin.ModelAdmin):
    list_display = ('tour', 'customer', 'overall_rating', 'status', 'verified_booking', 'is_featured', 'created_at')
    list_filter = ('status', 'overall_rating', 'verified_booking', 'is_featured', 'created_at')
    search_fields = ('tour__title', 'customer__user__username', 'title', 'review')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ('review', 'customer', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')
    search_fields = ('review__tour__title', 'customer__user__username')
    readonly_fields = ('created_at',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('customer', 'tour', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer__user__username', 'tour__title')
    readonly_fields = ('created_at',)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'valid_from', 'valid_until', 'used_count', 'is_active', 'created_at')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'created_at')
    search_fields = ('code', 'description', 'description_dk')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'customer', 'booking', 'discount_amount', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('coupon__code', 'customer__user__username', 'booking__booking_number')
    readonly_fields = ('used_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'notification_type', 'title', 'is_sent', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_sent', 'is_read', 'created_at')
    search_fields = ('customer__user__username', 'title', 'message')
    readonly_fields = ('created_at',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'view_count', 'published_at', 'created_at')
    list_filter = ('status', 'is_featured', 'category', 'published_at', 'created_at')
    search_fields = ('title', 'title_dk', 'slug', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'created_at', 'updated_at')

@admin.register(TourView)
class TourViewAdmin(admin.ModelAdmin):
    list_display = ('tour', 'customer', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('tour__title', 'customer__user__username', 'ip_address')
    readonly_fields = ('viewed_at',)

@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ('search_query', 'customer', 'results_count', 'ip_address', 'searched_at')
    list_filter = ('searched_at',)
    search_fields = ('search_query', 'customer__user__username')
    readonly_fields = ('searched_at',)

@admin.register(CustomerMessage)
class CustomerMessageAdmin(admin.ModelAdmin):
    list_display = ('customer', 'subject', 'sender_type', 'is_read', 'created_at')
    list_filter = ('sender_type', 'is_read', 'created_at')
    search_fields = ('subject', 'message', 'customer__user__username', 'customer__user__email')
    readonly_fields = ('created_at', 'updated_at', 'read_at')
    
    def get_customer(self, obj):
        return obj.customer.user.username
    get_customer.short_description = 'Customer'

@admin.register(FeatureSection)
class FeatureSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'rank', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'title_dk', 'short_description', 'description')

@admin.register(FeatureSectionTour)
class FeatureSectionTourAdmin(admin.ModelAdmin):
    list_display = ('feature_section', 'tour', 'created_at')
    list_filter = ('feature_section', 'created_at')
    search_fields = ('feature_section__title', 'tour__title')

@admin.register(WebsiteMenu)
class WebsiteMenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'section_type', 'rank', 'status', 'is_open_new_tab', 'created_at', 'updated_at')
    list_filter = ('section_type', 'status', 'created_at')
    search_fields = ('title', 'title_dk', 'link')

@admin.register(WebsiteSubMenu)
class WebsiteSubMenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'menu', 'rank', 'status', 'created_at')
    list_filter = ('menu', 'status', 'created_at')
    search_fields = ('title', 'title_dk', 'link', 'menu__title')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('qus_en', 'is_featured', 'status', 'display_order', 'created_at', 'updated_at')
    list_filter = ('is_featured', 'status', 'created_at')
    search_fields = ('qus_en', 'qus_dk', 'ans_en', 'ans_dk')
    list_editable = ('is_featured', 'status', 'display_order')
    readonly_fields = ('created_at', 'updated_at')
