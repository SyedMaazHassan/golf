from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserForm
import csv
from django.db import transaction
from django.contrib.auth.models import User

@login_required
def create_bulk_users(request):
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to import users")
        return redirect("home")

    if request.POST:
        csv_file = request.FILES['user-csv-file']
        if csv_file:
            csv_reader = csv.reader(csv_file.read().decode('utf-8').splitlines())
            header = next(csv_reader)

            try:
                with transaction.atomic():
                    # Process each row in the CSV file
                    for row in csv_reader:
                        # Access data for each column in the row
                        member_id = row[0]
                        first_name = row[1]
                        last_name = row[2]
                        email = row[3]
                        password = row[4]
                        is_staff = row[5]

                        print(f"Member ID: {member_id}, First Name: {first_name}, Last Name: {last_name}, Email: {email}, Password: {password}, Is Staff: {is_staff}")

                        # User creation
                        new_user = User.objects.create(
                            username = member_id,
                            email = email,
                            first_name = first_name,
                            last_name = last_name,
                            password = password,
                            is_staff = is_staff
                        )
                        print(new_user)

                    messages.success(request, "Users have been imported successfully!")

            except Exception as e:
                messages.error(request, str(e))

    context = {
        'page': 'import-users'
    }
    return render(request, "import_users.html", context)


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