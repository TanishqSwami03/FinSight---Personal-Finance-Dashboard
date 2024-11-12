from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .forms import *

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        print("post request received !!")
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        print("user authenticated !!", user)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            print("user logged in ! ", user)
            return redirect('dashboard')  # Redirect to your dashboard or another page
        else:
            messages.error(request, "Invalid email or password.")
    
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

def forgot_login_password(request):
    return render(request, 'forgot-login-password.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            # Extract email from cleaned data
            email = form.cleaned_data['email']

            # Check if the email already exists
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists. Please choose another email.")
                return render(request, 'signup.html', {'form': form})

            # Check if passwords match
            if form.cleaned_data['password1'] == form.cleaned_data['password2']:
                # Save the user
                user = form.save()
                print("Account created successfully!")
                messages.success(request, "Account created successfully!")
                
                # Redirect to success page
                return redirect('signup-success')  # 'signup-success' is the name of the success page URL pattern
            
            else:
                messages.error(request, "Passwords do not match.")
                print("Passwords do not match.")

        else:
            messages.error(request, "There was an error with your submission. Please check your details.")
            print("Form submission error.")

    # Display the form for a GET request or invalid POST
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})


def signup_success(request):
    return render(request, 'signup-success.html', {})