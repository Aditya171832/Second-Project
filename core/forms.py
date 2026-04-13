from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Category, Profile
from django.core.validators import RegexValidator
import re

class BaseRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain an uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain a lowercase letter.")
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError("Password must contain a number.")
        return password

class FarmerRegistrationForm(BaseRegistrationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    pincode = forms.CharField(max_length=10, required=True)
    farm_size = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    farm_location = forms.CharField(max_length=200, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2',
                  'phone', 'address', 'city', 'state', 'pincode', 'farm_size', 'farm_location']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^[6-9]\d{9}$', phone):
            raise forms.ValidationError("Enter valid 10-digit Indian phone number.")
        return phone
    
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not re.match(r'^\d{6}$', pincode):
            raise forms.ValidationError("Enter valid 6-digit pincode.")
        return pincode
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'user_type': 'farmer',
                    'phone': self.cleaned_data['phone'],
                    'address': self.cleaned_data['address'],
                    'city': self.cleaned_data['city'],
                    'state': self.cleaned_data['state'],
                    'pincode': self.cleaned_data['pincode'],
                    'farm_size': self.cleaned_data['farm_size'],
                    'farm_location': self.cleaned_data['farm_location'],
                }
            )
        return user

class DealerRegistrationForm(BaseRegistrationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    pincode = forms.CharField(max_length=10, required=True)
    company_name = forms.CharField(max_length=200, required=True)
    business_address = forms.CharField(widget=forms.Textarea, required=True)
    gst_number = forms.CharField(max_length=15, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2',
                  'phone', 'address', 'city', 'state', 'pincode',
                  'company_name', 'business_address', 'gst_number']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^[6-9]\d{9}$', phone):
            raise forms.ValidationError("Enter valid 10-digit Indian phone number.")
        return phone
    
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not re.match(r'^\d{6}$', pincode):
            raise forms.ValidationError("Enter valid 6-digit pincode.")
        return pincode
    
    def clean_gst_number(self):
        gst = self.cleaned_data.get('gst_number')
        if not re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', gst):
            raise forms.ValidationError("Enter valid GST number.")
        if Profile.objects.filter(gst_number=gst).exists():
            raise forms.ValidationError("GST number already registered.")
        return gst
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'user_type': 'dealer',
                    'phone': self.cleaned_data['phone'],
                    'address': self.cleaned_data['address'],
                    'city': self.cleaned_data['city'],
                    'state': self.cleaned_data['state'],
                    'pincode': self.cleaned_data['pincode'],
                    'company_name': self.cleaned_data['company_name'],
                    'business_address': self.cleaned_data['business_address'],
                    'gst_number': self.cleaned_data['gst_number'],
                }
            )
        return user

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock_quantity',
                  'image', 'nitrogen_content', 'phosphorus_content', 
                  'potassium_content', 'suitable_crops', 'usage_instructions']

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=255, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    pincode = forms.CharField(max_length=10, required=True)
    phone = forms.CharField(max_length=15, required=True)
    payment_method = forms.ChoiceField(
        choices=[('card', 'Card'), ('upi', 'UPI'), ('cod', 'COD')],
        widget=forms.RadioSelect
    )