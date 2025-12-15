from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from accounts.models import Booking, BookingParticipant, Tour, Customer, TourPricing, TourSchedule, TourReview
from decimal import Decimal
import json

class TourReviewForm(forms.ModelForm):


    class Meta:
        model = TourReview
        fields = ['overall_rating', 'title', 'review']
        widgets = {
            'overall_rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title of your review'}),
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['overall_rating'].widget.attrs.update({'class': 'rating-selection'})


class FrontendBookingForm(forms.ModelForm):
    """Booking form for frontend customers"""

    # Additional fields for participant management
    participants_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    coupon_code = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter coupon code (optional)'
    }))

    # Override some fields for better UX
    tour_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True
        }),
        required=True
    )

    tour_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        required=False
    )

    contact_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full name',
            'required': True
        }),
        required=True
    )

    contact_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'required': True
        }),
        required=True
    )

    contact_phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number',
            'required': True
        }),
        required=True
    )

    special_requirements = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special requirements or dietary restrictions?'
        }),
        required=False
    )

    pickup_location = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pickup location (if applicable)'
        }),
        required=False
    )

    customer_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes'
        }),
        required=False
    )

    class Meta:
        model = Booking
        fields = [
            'tour', 'schedule', 'tour_date', 'tour_time',
            'contact_name', 'contact_email', 'contact_phone',
            'special_requirements', 'pickup_location', 'customer_notes'
        ]

    def __init__(self, *args, **kwargs):
        self.tour = kwargs.pop('tour', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.tour:
            # Set the tour field as hidden since we're booking for a specific tour
            self.fields['tour'].initial = self.tour
            self.fields['tour'].widget = forms.HiddenInput()

            # Filter schedules for this tour
            self.fields['schedule'].queryset = TourSchedule.objects.filter(
                tour=self.tour,
                status='available'
            ).order_by('date', 'start_time')

            # If no schedules, make it optional
            if not self.fields['schedule'].queryset.exists():
                self.fields['schedule'].required = False
        else:
            self.fields['tour'].queryset = Tour.objects.filter(status='active')

    def clean_tour_date(self):
        tour_date = self.cleaned_data.get('tour_date')
        if tour_date and self.tour:
            # Check if the date is in blackout dates
            from accounts.models import TourBlackoutDate
            blackout_dates = TourBlackoutDate.objects.filter(
                tour=self.tour
            ).filter(
                start_date__lte=tour_date,
                end_date__gte=tour_date
            )
            if blackout_dates.exists():
                raise ValidationError("This date is not available for booking.")

        return tour_date

    def clean(self):
        cleaned_data = super().clean()
        participants_data = self.data.get('participants_data')

        if not participants_data:
            raise ValidationError("At least one participant is required.")

        try:
            participants = json.loads(participants_data)
            if not participants:
                raise ValidationError("At least one participant is required.")
        except (json.JSONDecodeError, TypeError):
            raise ValidationError("Invalid participant data.")

        return cleaned_data


class ParticipantForm(forms.Form):
    """Form for individual participant details"""
    participant_type = forms.ChoiceField(
        choices=[
            ('adult', 'Adult'),
            ('child', 'Child (2-12 years)'),
            ('infant', 'Infant (0-2 years)')
        ],
        widget=forms.Select(attrs={'class': 'form-select participant-type'})
    )

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'required': True
        })
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
            'required': True
        })
    )

    age = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Age',
            'min': 0,
            'max': 100
        }),
        required=False
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email (optional)'
        }),
        required=False
    )

    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone (optional)'
        }),
        required=False
    )

    special_requirements = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Special requirements (optional)'
        }),
        required=False
    )


