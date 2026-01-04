from django import forms
from django.contrib.auth.models import User
from .models import Customer, CustomerMessage, TourSupplier
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