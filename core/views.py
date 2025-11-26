from django.shortcuts import render
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Profile


def home(request):
    context = {"year": datetime.now().year}
    return render(request, "home.html", context)

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'STUDENT')  # 'ADMIN' or 'STUDENT'

        # basic validation
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )
        Profile.objects.create(user=user, role=role)

        messages.success(request, "Account created. You can now log in.")
        return redirect('login')

    return render(request, 'auth_register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'auth_login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

@login_required
def dashboard_view(request):
    # simple example dashboard for any logged-in user
    return render(request, 'dashboard.html')

def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'ADMIN'


@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    # basic admin-only page
    return render(request, 'admin_dashboard.html')
