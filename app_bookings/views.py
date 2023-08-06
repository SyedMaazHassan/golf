from django.shortcuts import render, redirect
from django.http import JsonResponse
from faker import Faker
from .models import *
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from datetime import datetime, date, timedelta
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json
from django.db import transaction
from django.conf import settings

max_booking_limit = settings.MAX_BOOKING_LIMIT

def run_cron_job():
    yesterday = date.today() - timedelta(days=1)

    # Check if yesterday's date is already present in CronJob model
    if not CronJob.objects.filter(date=yesterday).exists():
        print("Running")
        # Update all bookings with yesterday's date to 'completed' status
        Booking.objects.filter(date__lt=date.today()).update(status='completed')

        # Create a new entry in CronJob model for yesterday's date
        CronJob.objects.create(date=yesterday, is_run=True)
    else:
        print("Not running")



@login_required
def go_to_booking(request, booking_id):
    booking = Booking.objects.filter(id = booking_id).first()
    if not booking:
        return redirect("bays", bay_type="indoor")
    
    booked_slot = booking.slot
    bay_type = booked_slot.bay.type
    slot_id = f"slot_{booked_slot.id}"
    date = booking.date

    url = reverse('bays', args=[bay_type])
    absolute_url = request.build_absolute_uri(url) + f"?date={date.strftime('%Y-%m-%d')}&slot_id={slot_id}"
    return redirect(absolute_url)



@login_required
def delete_booking(request, booking_id):
    booking = Booking.objects.filter(id = booking_id).first()    
    if not booking:
        return redirect("bays", bay_type="indoor")
    
    if booking.user == request.user:
        booking.delete()
        messages.success(request, "Booking has been deleted successfully!")
    else:
        messages.error(request, "You don't have permission to delete this booking!")

    return redirect("my-bookings")



@login_required
def my_bookings_view(request):
    context = {
        'page':'bookings'
    }
    bookings = Booking.objects.filter(user = request.user)

    date_filter = request.GET.get('date')
    if date_filter:
        my_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        bookings = bookings.filter(date = my_date)    

    context['bookings'] = bookings
    return render(request, "bookings.html", context)



def submit_bookings(request):
    output = {'status': True, 'msg': None}
    if not request.user.is_authenticated:
        output['msg'] = 'User is not authenticated'
        output['status'] = False
        return JsonResponse(output)


    data = request.GET.get('data')
    date_filter = request.GET.get('date')
    bay_type = request.GET.get('bay_type')
    today = date.today()
    if date_filter:
        my_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    else:
        my_date = timezone.now().date()
    data = json.loads(data)

    # Fetching user bookings
    all_user_bookings = Booking.objects.filter(user = request.user, date = my_date).exclude(status='cancelled')
    all_user_bookings_count = all_user_bookings.count()


    try:
        with transaction.atomic():
            for booking in data:
                slot = booking['slot_id']
                bay = booking['bay_id']
            
                slot_object = Slot.objects.filter(id = slot).first()
                bay_object = Bay.objects.filter(id = bay).first()

                if slot_object and bay_object and slot_object.bay == bay_object:
                    checking_booking = Booking.objects.filter(date = my_date, slot = slot_object, status='booked').exists()
                    if checking_booking:
                        messages.error(request, "This slot has already been booked!")
                        return redirect("bays", bay_type=bay_type)
                    
                    # Second check if user has already booked 6 slots for a perticular day
                    if all_user_bookings_count == max_booking_limit:
                        messages.error(request, f"Booking limit ({max_booking_limit} bookings) reached for the date {my_date}, Kindly select any other date!")
                        return redirect("bays", bay_type=bay_type)

                    # Create booking
                    new_booking = Booking(
                        user = request.user,
                        slot = slot_object,
                        date = my_date
                    )

                    try:
                        new_booking.validate_date_and_time()
                        new_booking.save()
                        output['status'] = True
                        output['msg'] = 'Selected slot(s) booked successfully'
                        print(new_booking, "created")

                    except Exception as e:

                        output['msg'] = str(e)
                        output['status'] = False
                        return JsonResponse(output)
                    
    except Exception as e:
        output['msg'] = str(e)
        output['status'] = False
        return JsonResponse(output)

    return JsonResponse(output)


@login_required
def bays_view(request, bay_type):
    if bay_type not in ['indoor', 'outdoor']:
        return redirect("bays", bay_type='indoor')

    # cron job
    run_cron_job()

    date_filter = request.GET.get('date')
    today = date.today()
    if date_filter:
        my_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    else:
        my_date = timezone.now().date()

    all_user_bookings = Booking.objects.filter(user = request.user, date = my_date).exclude(status='cancelled')
    all_user_bookings_count = all_user_bookings.count()
    current_user = request.user



    context = {
        'is_staff': json.dumps(current_user.is_superuser or current_user.is_staff),
        'today': today.strftime('%Y-%m-%d'),
        'date': my_date.strftime('%Y-%m-%d'),
        'date_to_show': my_date,
        'page': 'bays',
        'bay_type': bay_type,
        'all_user_bookings_count': all_user_bookings_count,
        'max_booking_limit': max_booking_limit
    }

    all_bays = Bay.objects.filter(type = bay_type)
    all_slots = Slot.objects.all()
    all_bookings = Booking.objects.filter(date = my_date, status='booked')
    only_user_bookings = all_bookings.filter(user = request.user)

    all_booking_list_format = all_bookings.values_list('slot_id', flat=True)
    only_user_bookings_list_format = only_user_bookings.values_list('slot_id', flat=True)
    current_time = timezone.now().time()
    for bay in all_bays:
        bay.all_slots = all_slots.filter(bay = bay)
        for slot in bay.all_slots:
            if my_date > today or current_time < slot.start_time:
                slot.is_slot_available = True
            else:
                slot.is_slot_available = False

            if slot.id in all_booking_list_format:
                slot.is_booked = True
                slot.is_mine = False
                if slot.id in only_user_bookings_list_format:
                    slot.is_mine = True
    

    context["bays"] = all_bays
    return render(request, "bays.html", context)


@login_required
def home_view(request):
    return redirect("bays", bay_type="indoor")
