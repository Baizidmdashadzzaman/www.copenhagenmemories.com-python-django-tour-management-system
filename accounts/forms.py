from django import forms
from django.contrib.auth.models import User
from .models import Customer, CustomerMessage, TourSupplier, Tour
from django.contrib.auth.forms import AuthenticationForm

class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg pass-input', 'placeholder': 'Enter Password'})
    )
    phone = forms.CharField(
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Phone Number'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Address', 'rows': 3}), 
        required=False
    )

    class Meta:
        model = Customer
        fields = ['phone', 'address']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        customer = super().save(commit=False)
        customer.user = user
        if commit:
            customer.save()
        return customer

class AdminRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            is_staff=True 
        )
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or Email', 
        widget=forms.TextInput(attrs={
            'autofocus': True, 
            'class': 'form-control form-control-lg', 
            'placeholder': 'Enter Username or Email'
        })
    )
    password = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg pass-input', 
            'placeholder': 'Enter Password'
        })
    )


class CustomerProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    phone = forms.CharField(
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'})
    )
    nationality = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nationality'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current password'}),
        help_text="Leave blank if you don't want to change it"
    )

    class Meta:
        model = Customer
        fields = ['phone', 'address', 'nationality', 'date_of_birth', 'profile_image']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, commit=True, user=None):
        customer = super().save(commit=False)
        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            
            new_password = self.cleaned_data.get('new_password')
            if new_password:
                user.set_password(new_password)
            
            if commit:
                user.save()
                customer.save()
        return customer

class CustomerMessageForm(forms.ModelForm):
    subject = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Type your message here...'})
    )

    class Meta:
        model = CustomerMessage
        fields = ['subject', 'message']

class TourSupplierRegistrationForm(forms.ModelForm):
    company_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Company Name'})
    )
    contact_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Contact Person Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg pass-input', 'placeholder': 'Enter Password'})
    )
    phone = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Phone Number'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Address', 'rows': 3}),
        required=True
    )

    class Meta:
        model = TourSupplier
        fields = ['company_name', 'contact_name', 'email', 'phone', 'address']

    def clean_email(self):
        email = self.cleaned_data['email']
        if TourSupplier.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def save(self, commit=True):
        supplier = super().save(commit=False)
        supplier.password = self.cleaned_data['password']  # Note: Storing plain text as per implied system design, but ideally should be hashed
        # Set default status to active or pending? User didn't specify. Model default is 'active'.
        if commit:
            supplier.save()
        return supplier

class TourSupplierLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg pass-input', 'placeholder': 'Enter Password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                supplier = TourSupplier.objects.get(email=email)
                if supplier.password != password: # NOTE: Using plain text comparison as hashed password implementation is pending
                     raise forms.ValidationError("Invalid email or password.")
                cleaned_data['supplier'] = supplier
            except TourSupplier.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")
        
        return cleaned_data

class TourSupplierProfileUpdateForm(forms.ModelForm):
    company_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'})
    )
    contact_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    phone = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3})
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website URL'})
    )
    tax_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tax ID'})
    )
    payment_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Payment Details', 'rows': 3})
    )
    bank_account = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Account'})
    )
    other_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Other Details', 'rows': 3})
    )
    logo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current password'}),
        help_text="Leave blank if you don't want to change it"
    )

    class Meta:
        model = TourSupplier
        fields = ['company_name', 'contact_name', 'email', 'phone', 'address', 'city', 'country', 'website', 'tax_id', 'payment_details', 'bank_account', 'other_details', 'logo']
        widgets = {
            'country': forms.Select(attrs={'class': 'form-control form-select'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if TourSupplier.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def save(self, commit=True):
        supplier = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            supplier.password = new_password
        
        if commit:
            supplier.save()
        return supplier

class SupplierTourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = [
            'title', 'title_dk', 'category', 'destination_region', 'city', 
            'short_description', 'short_description_dk', 'description', 'description_dk',
            'main_image', 'video_url', 
            'duration_hours', 'duration_text', 'min_participants', 'max_participants', 
            'age_restriction', 'difficulty_level',
            'base_price', 'currency', 'discount_percentage',
            'meeting_point', 'meeting_point_dk', 'meeting_point_latitude', 'meeting_point_longitude', 'map_location',
            'start_date', 'end_date',
            'instant_confirmation', 'free_cancellation', 'cancellation_hours', 'mobile_ticket', 
            'skip_the_line', 'live_guide', 'audio_guide', 'wheelchair_accessible',
            'meta_title', 'meta_description', 'meta_keywords'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tour Title'}),
            'title_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tour Title (DK)'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'destination_region': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Short Description'}),
            'short_description_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Short Description (DK)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Full Description'}),
            'description_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Full Description (DK)'}),
            
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Video URL'}),
            
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Hours'}),
            'duration_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2 Hours'}),
            'min_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'age_restriction': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 18+'}),
            'difficulty_level': forms.Select(attrs={'class': 'form-select'}),
            
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'value': 'DKK', 'readonly': True}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0, 'max': 100}),
            
            'meeting_point': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Meeting Point'}),
            'meeting_point_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Meeting Point (DK)'}),
            'meeting_point_latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'meeting_point_longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'map_location': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Google Maps Embed URL'}),
            
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cancellation_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            
            'instant_confirmation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'free_cancellation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mobile_ticket': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'skip_the_line': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'live_guide': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'audio_guide': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wheelchair_accessible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            'meta_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Meta Title'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Meta Description'}),
            'meta_keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Meta Keywords'}),
        }

