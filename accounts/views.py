from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import User
from .forms import ProfileEditForm, PasswordChangeForm


def root_redirect(request):
    """Redirect root URL based on authentication status."""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    else:
        return redirect('accounts:login')


def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        errors = []
        
        # Validate email
        if not email:
            errors.append('Email is required.')
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Please enter a valid email address.')
        
        # Validate password
        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        elif password.isdigit():
            errors.append('Password cannot be entirely numeric.')
        
        # Check password confirmation
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            errors.append('A user with this email already exists.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/register.html', {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            })
        
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Daily Discipline OS.')
            return redirect('dashboard:dashboard')
        except IntegrityError:
            messages.error(request, 'A user with this email already exists.')
            return render(request, 'accounts/register.html', {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            })
    
    return render(request, 'accounts/register.html')


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Please enter both email and password.')
            return render(request, 'accounts/login.html', {'email': email})
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:dashboard')
            messages.success(request, f'Welcome back!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
            return render(request, 'accounts/login.html', {'email': email})
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def toggle_theme(request):
    """Toggle between light and dark mode."""
    if request.method == 'POST':
        current_theme = request.user.theme_preference
        new_theme = 'dark' if current_theme == 'light' else 'light'
        request.user.theme_preference = new_theme
        request.user.save()
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'theme': new_theme})
        
        # Redirect for regular form submissions
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'dashboard:dashboard'))
        return redirect(next_url)
    
    return redirect('dashboard:dashboard')


@login_required
def profile_view(request):
    """Display user profile."""
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_edit_view(request):
    """Edit user profile."""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def password_change_view(request):
    """Change user password."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})