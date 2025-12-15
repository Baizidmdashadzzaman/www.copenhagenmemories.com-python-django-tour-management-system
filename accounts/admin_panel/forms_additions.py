from django import forms
from accounts.models import BlogPost, Category, City, Tour, Coupon, Booking, Payment, TourReview, TourImage, TourHighlight, TourIncluded, TourExcluded, TourItinerary, TourRequirement, TourFAQ, TourPricing, TourSchedule, TourBlackoutDate, BookingParticipant

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'title_dk', 'category', 'featured_image', 'excerpt', 'excerpt_dk', 
                  'content', 'content_dk', 'meta_title', 'meta_description', 'meta_keywords', 
                  'status', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'title_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Danish title'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter excerpt'}),
            'excerpt_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter Danish excerpt'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Enter content'}),
            'content_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Enter Danish content'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meta_keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', 'name_dk', 'region', 'country', 'description', 'description_dk', 'image', 'latitude', 'longitude', 'is_popular', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city name'}),
            'name_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Danish city name'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description'}),
            'description_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter Danish description'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'is_popular': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = ['title', 'title_dk', 'supplier', 'category', 'destination_region', 'city', 'short_description', 'short_description_dk', 'description', 'description_dk', 'map_location', 'main_image', 'video_url', 'duration_hours', 'duration_text', 'min_participants', 'max_participants', 'age_restriction', 'difficulty_level', 'base_price', 'currency', 'discount_percentage', 'status', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter tour title'}),
            'title_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Danish tour title'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'destination_region': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter short description'}),
            'short_description_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter Danish short description'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Enter full description'}),
            'description_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Enter Danish description'}),
            'map_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Google Maps Embed URL'}),
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
            'video_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter video URL'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Duration in hours'}),
            'duration_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2-3 hours'}),
            'min_participants': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control'}),
            'age_restriction': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Age restriction if any'}),
            'difficulty_level': forms.Select(attrs={'class': 'form-select'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'discount_value', 'max_discount_amount', 'min_purchase_amount', 'usage_per_customer', 'usage_limit', 'valid_from', 'valid_until', 'is_active', 'description', 'description_dk']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter coupon code'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Discount value'}),
            'max_discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Max discount amount'}),
            'min_purchase_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Minimum purchase amount'}),
            'usage_per_customer': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Uses per customer'}),
            'usage_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total usage limit'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter coupon description'}),
            'description_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter Danish coupon description'}),
        }


class BookingForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label='Customer'
    )
    tour = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label='Tour'
    )
    schedule = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label='Schedule (Optional)'
    )
    
    class Meta:
        model = Booking
        fields = ['customer', 'tour', 'schedule', 'tour_date', 'tour_time', 'total_participants', 
                  'contact_name', 'contact_email', 'contact_phone', 'special_requirements', 
                  'pickup_location', 'subtotal', 'discount_amount', 'tax_amount', 'total_amount',
                  'status', 'payment_status', 'customer_notes', 'admin_notes']
        widgets = {
            'tour_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tour_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'total_participants': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact name'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Contact email'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact phone'}),
            'special_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Special requirements'}),
            'pickup_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pickup location'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'customer_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Customer notes'}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Admin notes'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import Customer, Tour, TourSchedule
        
        # Set querysets
        self.fields['customer'].queryset = Customer.objects.select_related('user').all()
        self.fields['tour'].queryset = Tour.objects.filter(status='active')
        self.fields['schedule'].queryset = TourSchedule.objects.filter(status='available')
        
        # If editing existing booking, filter schedule by tour
        if self.instance and self.instance.pk and self.instance.tour:
            self.fields['schedule'].queryset = TourSchedule.objects.filter(
                tour=self.instance.tour,
                status='available'
            )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'amount', 'status', 'refund_reason']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'refund_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Refund reason if applicable'}),
        }


class TourReviewForm(forms.ModelForm):
    class Meta:
        model = TourReview
        fields = ['overall_rating', 'value_rating', 'service_rating', 'organization_rating', 'title', 'review', 'status', 'is_featured', 'supplier_response']
        widgets = {
            'overall_rating': forms.Select(attrs={'class': 'form-select'}),
            'value_rating': forms.Select(attrs={'class': 'form-select'}),
            'service_rating': forms.Select(attrs={'class': 'form-select'}),
            'organization_rating': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Review title'}),
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter review'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'supplier_response': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Supplier response'}),
        }


class TourImageForm(forms.ModelForm):
    class Meta:
        model = TourImage
        fields = ['image', 'caption', 'caption_dk', 'display_order', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image caption (English)'}),
            'caption_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image caption (Danish)'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Display order'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TourHighlightForm(forms.ModelForm):
    class Meta:
        model = TourHighlight
        fields = ['highlight', 'highlight_dk', 'icon', 'display_order']
        widgets = {
            'highlight': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Highlight text (English)'}),
            'highlight_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Highlight text (Danish)'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Icon class (e.g., ti tabler-check)'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Display order'}),
        }


class TourIncludedForm(forms.ModelForm):
    class Meta:
        model = TourIncluded
        fields = ['item', 'item_dk', 'display_order']
        widgets = {
            'item': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Included item (English)'}),
            'item_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Included item (Danish)'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Display order'}),
        }


class TourExcludedForm(forms.ModelForm):
    class Meta:
        model = TourExcluded
        fields = ['item', 'item_dk', 'display_order']
        widgets = {
            'item': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Excluded item (English)'}),
            'item_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Excluded item (Danish)'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Display order'}),
        }


class TourItineraryForm(forms.ModelForm):
    class Meta:
        model = TourItinerary
        fields = ['step_number', 'title', 'title_dk', 'description', 'description_dk', 'duration_minutes', 'location', 'latitude', 'longitude']
        widgets = {
            'step_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Step number'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Step title (English)'}),
            'title_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Step title (Danish)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description (English)'}),
            'description_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description (Danish)'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration in minutes'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location name'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
        }


class TourRequirementForm(forms.ModelForm):
    class Meta:
        model = TourRequirement
        fields = ['requirement', 'requirement_dk', 'is_mandatory', 'display_order']
        widgets = {
            'requirement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Requirement (English)'}),
            'requirement_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Requirement (Danish)'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Display order'}),
        }


class TourFAQForm(forms.ModelForm):
    class Meta:
        model = TourFAQ
        fields = ['question', 'question_dk', 'answer', 'answer_dk', 'display_order']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Question (English)'}),
            'question_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Question (Danish)'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Answer (English)'}),
            'answer_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Answer (Danish)'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Display order'}),
        }


class TourPricingForm(forms.ModelForm):
    class Meta:
        model = TourPricing
        fields = ['participant_type', 'min_age', 'max_age', 'price', 'currency', 'description', 'description_dk', 'is_active']
        widgets = {
            'participant_type': forms.Select(attrs={'class': 'form-select'}),
            'min_age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min age'}),
            'max_age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max age'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Price'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Currency'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description (English)'}),
            'description_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description (Danish)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TourScheduleForm(forms.ModelForm):
    class Meta:
        model = TourSchedule
        fields = ['date', 'start_time', 'end_time', 'available_slots', 'booked_slots', 'price_override', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'available_slots': forms.NumberInput(attrs={'class': 'form-control'}),
            'booked_slots': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_override': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TourBlackoutDateForm(forms.ModelForm):
    class Meta:
        model = TourBlackoutDate
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason'}),
        }
