# Generated by Django 4.2 on 2023-08-21 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_bookings', '0003_cronjob'),
    ]

    operations = [
        migrations.AddField(
            model_name='bay',
            name='number',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
