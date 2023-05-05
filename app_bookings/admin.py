from django.contrib import admin
from .models import *
from .views import run_cron_job
# Register your models here.


admin.site.register(Bay)
admin.site.register(Slot)

class BookingAdmin(admin.ModelAdmin):
    # other fields and options for the admin class
    # search_fields = ['id', 'date', 'status', 'user']
    actions = ['run_cron_job_action']
    list_display = ['id', 'date', 'slot', 'status', 'user', 'created_at']

    def run_cron_job_action(self, request, queryset):
        run_cron_job()
        self.message_user(request, 'Cron job has been run for yesterday')

    run_cron_job_action.short_description = 'Run cron job for yesterday'

class CronJobAdmin(admin.ModelAdmin):
    # other fields and options for the admin class

    actions = ['run_cron_job_action']
    list_display = ['date', 'is_run']

    def run_cron_job_action(self, request, queryset):
        run_cron_job()
        self.message_user(request, 'Cron job has been run for yesterday')
    run_cron_job_action.short_description = 'Run cron job for yesterday'


admin.site.register(Booking, BookingAdmin)
admin.site.register(CronJob, CronJobAdmin)