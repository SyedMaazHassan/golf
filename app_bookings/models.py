from django.db import models
import time
from django.contrib.auth.models import User
from datetime import time, timedelta, datetime, date
from django.utils import timezone
from django.core.exceptions import ValidationError
# Create your models here.

# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver

class CronJob(models.Model):
    date = models.DateField()
    is_run = models.BooleanField()


class Bay(models.Model):
    start_service_time = models.TimeField(default=time(9, 0))
    end_service_time = models.TimeField(default=time(17, 0))
    type = models.CharField(max_length=10, choices=[('indoor', 'Indoor'), ('outdoor', 'Outdoor')])

    def get_slots(self):
        all_slots = Slot.objects.filter(bay = self)
        return all_slots

    def __str__(self):
        return f'{self.pk}'


class Slot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    bay = models.ForeignKey(Bay, on_delete=models.CASCADE)

    def __str__(self):
        start_time_str = self.start_time.strftime('%I:%M %p')
        end_time_str = self.end_time.strftime('%I:%M %p')
        return f'{start_time_str} - {end_time_str}'


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, 
        choices=[('booked', 'Booked'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], 
        default='booked'
    )
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(default=timezone.now)

    def validate_date_and_time(self):
        """
        Custom validation method to ensure that the booking date and slot end time are not in the past.
        """
        if self.date < date.today():
            raise ValidationError("Booking date cannot be in the past.")

        if timezone.make_aware(datetime.combine(self.date, self.slot.end_time)) < timezone.now():
            raise ValidationError("Booking slot end time cannot be in the past.")

    def __str__(self):
        return f'{self.date} / Bay # {self.slot.bay} / {self.slot} (By {self.user})'

    class Meta:
        ordering = ("-date", "-id")
