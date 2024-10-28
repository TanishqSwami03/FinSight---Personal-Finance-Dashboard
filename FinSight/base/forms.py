from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # Assuming you have a custom user model

class CustomUserCreationForm(UserCreationForm):
    COUNTRY_CODES = [
        ('+91', '+91'),
    ]

    mobile_code = forms.ChoiceField(choices=COUNTRY_CODES)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'mobile_code', 'mobile_number', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'First Name'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Last Name'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Email Address'
        })
        self.fields['mobile_code'].widget.attrs.update({
            'class': 'form-select', 'id': 'code'
        })
        self.fields['mobile_number'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Phone Number'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Confirm Password'
        })