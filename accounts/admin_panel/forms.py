from django import forms
from accounts.models import DestinationRegion, SiteSetting, Country, Customer, TourSupplier, Category, Slider, Newsletter, ContactUs, CustomerReviewStatic, Page, BlogPost, CustomerMessage, FeatureSection, WebsiteMenu, WebsiteSubMenu, FAQ
from django.contrib.auth.models import User, Group

class CustomerForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150, 
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter username',
            'style': 'width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter email address',
            'style': 'width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;'
        })
    )
    first_name = forms.CharField(
        max_length=150, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter first name',
            'style': 'width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;'
        })
    )
    last_name = forms.CharField(
        max_length=150, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter last name',
            'style': 'width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter password',
            'style': 'width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;'
        }), 
        required=False, 
        help_text='Leave blank to keep current password'
    )
    
    class Meta:
        model = Customer
        fields = ['phone', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={
                'placeholder': 'Enter phone number',
                'style': 'width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Enter address',
                'style': 'width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True
    
    def save(self, commit=True):
        customer = super().save(commit=False)
        
        if self.instance.pk:
            user = self.instance.user
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()
        else:
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                password=self.cleaned_data['password']
            )
            customer.user = user
        
        if commit:
            customer.save()
        return customer

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name', 'code', 'flag_image', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter country name'}),
            'code': forms.TextInput(attrs={'placeholder': 'Enter country code (e.g. DK, US)'}),
            'flag_image': forms.FileInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class DestinationRegionForm(forms.ModelForm):
    class Meta:
        model = DestinationRegion
        fields = ['name', 'description', 'country', 'image', 'cover_image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter region name'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter description'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = [
            'site_name', 'site_logo', 'site_favicon', 'site_email', 
            'site_address', 'site_description', 'site_metakey', 'site_metadescription','site_phone',
            'site_map','app_google','ios_app','fb_link','x_link','insta_link','linkdin_link','pintrest_link','site_logo_dark'
        ]
        widgets = {
            'site_name': forms.TextInput(attrs={'placeholder': 'Enter site name'}),
            'site_phone': forms.TextInput(attrs={'placeholder': 'Enter site phone'}),
            'site_email': forms.EmailInput(attrs={'placeholder': 'contact@example.com'}),
            'site_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter site address'}),
            'site_description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter site description'}),
            'site_metakey': forms.Textarea(attrs={'rows': 2, 'placeholder': 'keyword1, keyword2, keyword3'}),
            'site_metadescription': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter meta description'}),
            'site_map': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter site map'}),
            'app_google': forms.TextInput(attrs={'placeholder': 'Enter app google link'}),
            'ios_app': forms.TextInput(attrs={'placeholder': 'Enter ios app link'}),
            'fb_link': forms.TextInput(attrs={'placeholder': 'Enter fb link'}),
            'x_link': forms.TextInput(attrs={'placeholder': 'Enter x link'}),
            'insta_link': forms.TextInput(attrs={'placeholder': 'Enter insta link'}),
            'linkdin_link': forms.TextInput(attrs={'placeholder': 'Enter linkdin link'}),
            'pintrest_link': forms.TextInput(attrs={'placeholder': 'Enter pintrest link'}),
        }

class TourSupplierForm(forms.ModelForm):
    class Meta:
        model = TourSupplier
        fields = [
            'company_name', 'contact_name', 'email', 'phone', 'address', 
            'city', 'country', 'website', 'logo', 'tax_id', 'payment_details', 
            'bank_account', 'commission_rate', 'rating', 'total_reviews', 
            'verified', 'status', 'other_details'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'placeholder': 'Enter company name'}),
            'contact_name': forms.TextInput(attrs={'placeholder': 'Enter contact person name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email address'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter address'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter city'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'website': forms.URLInput(attrs={'placeholder': 'Enter website URL'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'other_details': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter other details'}),
            'tax_id': forms.TextInput(attrs={'placeholder': 'Enter tax ID'}),
            'payment_details': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter payment details'}),
            'bank_account': forms.TextInput(attrs={'placeholder': 'Enter bank account details'}),
            'commission_rate': forms.NumberInput(attrs={'placeholder': 'Enter commission rate (%)', 'step': '0.01'}),
            'rating': forms.NumberInput(attrs={'placeholder': 'Enter rating (0-5)', 'step': '0.01', 'min': '0', 'max': '5'}),
            'total_reviews': forms.NumberInput(attrs={'placeholder': 'Enter total reviews', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-select', 'id': 'id_status'}),
            'verified': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_verified'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'name_dk', 'image', 'description', 'description_dk', 'status', 'other_info']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter category name', 'class': 'form-control'}),
            'name_dk': forms.TextInput(attrs={'placeholder': 'Enter Danish category name', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter description', 'class': 'form-control'}),
            'description_dk': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter Danish description', 'class': 'form-control'}),
            'other_info': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter other info', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class SliderForm(forms.ModelForm):
    class Meta:
        model = Slider
        fields = ['title', 'title_dk', 'subtitle', 'subtitle_dk', 'image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter slider title', 'class': 'form-control'}),
            'title_dk': forms.TextInput(attrs={'placeholder': 'Enter Danish slider title', 'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'placeholder': 'Enter slider subtitle', 'class': 'form-control'}),
            'subtitle_dk': forms.TextInput(attrs={'placeholder': 'Enter Danish slider subtitle', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email address', 'class': 'form-control'}),
        }

class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'phone', 'subject', 'message', 'is_notified']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email address', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter phone number', 'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Enter subject', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter message', 'class': 'form-control'}),
            'is_notified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }        


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter group name', 'class': 'form-control'}),
            'permissions': forms.SelectMultiple(attrs={'class': 'form-select', 'style': 'height: 300px;'}),
        }

class AdminUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False, help_text="Leave empty to keep current password")
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser', 'groups', 'user_permissions']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'user_permissions': forms.SelectMultiple(attrs={'class': 'form-select', 'style': 'height: 300px;'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            self.save_m2m()
        return user


class CustomerReviewStaticForm(forms.ModelForm):
    class Meta:
        model = CustomerReviewStatic
        fields = ['name', 'address', 'image', 'review', 'review_dk', 'rating', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter reviewer name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter reviewer address'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter review'}),
            'review_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter review in Danish'}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'title_dk', 'image', 'content', 'content_dk', 'display_section', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter page title'}),
            'title_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Danish page title'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter page content'}),
            'content_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter Danish page content'}),
            'display_section': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CustomerMessageForm(forms.ModelForm):
    class Meta:
        model = CustomerMessage
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter message subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Enter your message'}),
        }

class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = CustomerMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your reply'}),
        }


class FeatureSectionForm(forms.ModelForm):
    class Meta:
        model = FeatureSection
        fields = ['title', 'title_dk', 'banner', 'is_banner_showing', 'short_description', 'short_description_dk', 'description', 'description_dk', 'status', 'rank']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'title_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title in Danish'}),
            'banner': forms.FileInput(attrs={'class': 'form-control'}),
            'is_banner_showing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter short description'}),
            'short_description_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter short description in Danish'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description'}),
            'description_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description in Danish'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'rank': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter rank'}),
        }

class WebsiteMenuForm(forms.ModelForm):
    class Meta:
        model = WebsiteMenu
        fields = ['title', 'title_dk', 'banner', 'is_banner_showing', 'section_type', 'status', 'rank', 'link', 'is_open_new_tab', 'has_submenu']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'title_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title in Danish'}),
            'banner': forms.FileInput(attrs={'class': 'form-control'}),
            'is_banner_showing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'section_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'rank': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter rank'}),
            'link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter link/url'}),
            'is_open_new_tab': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_submenu': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class WebsiteSubMenuForm(forms.ModelForm):
    class Meta:
        model = WebsiteSubMenu
        fields = ['title', 'title_dk', 'status', 'rank', 'link', 'is_open_new_tab']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'title_dk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title in Danish'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'rank': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter rank'}),
            'link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter link/url'}),
            'is_open_new_tab': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['qus_en', 'qus_dk', 'ans_en', 'ans_dk', 'is_featured', 'status', 'display_order']
        widgets = {
            'qus_en': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter question in English'}),
            'qus_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter question in Danish'}),
            'ans_en': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter answer in English'}),
            'ans_dk': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter answer in Danish'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter display order'}),
        }
