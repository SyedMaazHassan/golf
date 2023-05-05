from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserForm


@login_required
def profile_view(request):
    context = {
        'page': 'profile'
    }

    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        form = UserForm(instance=request.user)

    context['user_form'] = form
    return render(request, "profile.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        next = request.GET.get('next')
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if next:
                return redirect(next)

            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def reset_password_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            user = request.user
            user.set_password(password)
            user.save()
            messages.success(request, "Password has been reset successfully!")
        else:
            messages.error(request, "Password doesn't match!")

    return redirect("profile")