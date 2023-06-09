# Generated by Django 4.2 on 2023-05-03 15:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app_bookings', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'ordering': ('-date', '-id')},
        ),
        migrations.AddField(
            model_name='booking',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
