from django.db.models.signals import post_save
import datetime
from django.dispatch import receiver
from .models import Slot, Bay

@receiver(post_save, sender=Bay)
def create_slots(sender, instance, created, **kwargs):
    if created:
        service_start = instance.start_service_time
        service_end = instance.end_service_time
        slot_duration = datetime.timedelta(minutes=20)
        current_time = datetime.datetime.combine(datetime.date.today(), service_start)

        # Create slots with 20-minute gaps between start_service_time and end_service_time
        while current_time + slot_duration <= datetime.datetime.combine(datetime.date.today(), service_end):
            slot = Slot.objects.create(
                start_time=current_time.time(),
                end_time=(current_time + slot_duration).time(),
                bay = instance
            )
            current_time += slot_duration
