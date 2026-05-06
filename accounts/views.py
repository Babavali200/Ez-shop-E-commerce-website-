from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
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

def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("home")
