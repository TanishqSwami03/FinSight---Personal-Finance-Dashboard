from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import ReadOnlyPasswordHashField

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

class AdminUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class AdminUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password', 'is_active', 'is_staff', 'is_superuser')

    def clean_password(self):
        return self.initial["password"]
