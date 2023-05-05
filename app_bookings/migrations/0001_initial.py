# Generated by Django 4.2 on 2023-05-02 16:29

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_service_time', models.TimeField(default=datetime.time(9, 0))),
                ('end_service_time', models.TimeField(default=datetime.time(17, 0))),
                ('type', models.CharField(choices=[('indoor', 'Indoor'), ('outdoor', 'Outdoor')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_available', models.BooleanField(default=True)),
                ('bay', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_bookings.bay')),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('booked', 'Booked'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='booked', max_length=20)),
                ('date', models.DateField(default=datetime.date.today)),
                ('slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_bookings.slot')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
