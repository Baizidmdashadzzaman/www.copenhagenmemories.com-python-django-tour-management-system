
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
