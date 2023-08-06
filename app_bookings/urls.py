from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('bays/<str:bay_type>/', views.bays_view, name='bays'),
    path('bookings/', views.my_bookings_view, name='my-bookings'),
    path('bookings/<int:booking_id>', views.go_to_booking, name='single-booking'),
    path('bookings/<int:booking_id>/delete', views.delete_booking, name='delete-booking'),
    path('submit_bookings', views.submit_bookings, name='submit_bookings'),

]
