# Generated by Django 4.2 on 2023-05-03 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_bookings', '0002_alter_booking_options_booking_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='CronJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('is_run', models.BooleanField()),
            ],
        ),
    ]
