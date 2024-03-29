from django.db import models
import time
from django.contrib.auth.models import User
from datetime import time, timedelta, datetime, date
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver

class CronJob(models.Model):
    date = models.DateField()
    is_run = models.BooleanField()


class Bay(models.Model):
    number = models.IntegerField(null=True, blank=True, unique=True)
    start_service_time = models.TimeField(default=time(9, 0))
    end_service_time = models.TimeField(default=time(17, 0))
    type = models.CharField(max_length=10, choices=[('indoor', 'Indoor'), ('outdoor', 'Outdoor')])

    def get_slots(self):
        all_slots = Slot.objects.filter(bay = self)
        return all_slots

    def __str__(self):
        return f'{self.number}'


@receiver(post_save, sender=Bay)
def set_number_on_create(sender, instance, created, **kwargs):
    if created and not instance.number:
        instance.number = instance.id
        instance.save()


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

        # convert timezone.now() to a naive datetime object in the local timezone
        now_local = timezone.now().astimezone(timezone.get_current_timezone()).replace(tzinfo=None)

        if datetime.combine(self.date, self.slot.start_time) < now_local:
            raise ValidationError("Booking slot end time cannot be in the past.")



    def __str__(self):
        return f'{self.date} / Bay # {self.slot.bay} / {self.slot} (By {self.user})'

    class Meta:
        ordering = ("-date", "-id")
