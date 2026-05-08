from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.user_type == 'seller':
                user.is_approved = False
            user.save()
            
            if user.is_approved:
                login(request, user)
                messages.success(request, 'Registration successful. Welcome!')
                return redirect('home')
            else:
                messages.info(request, 'Registration successful. Please wait for admin approval before logging in.')
                return redirect('login')
        else:
            messages.error(request, 'Unsuccessful registration. Invalid information.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Admin/superuser → go to admin panel
            if user.is_superuser:
                login(request, user)
                return redirect('/admin/')
            
            # Seller not approved yet
            elif hasattr(user, 'user_type') and user.user_type == 'seller' and not user.is_approved:
                messages.error(request, 'Your seller account is pending admin approval.')
                return redirect('login')
            
            # Normal login
            else:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                if hasattr(user, 'user_type') and user.user_type == 'seller':
                    return redirect('seller_dashboard')  # change to your seller dashboard url name
                else:
                    return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("home")
