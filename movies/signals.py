from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking, Seat

# Signal to mark seat as booked when a booking is created
@receiver(post_save, sender=Booking)
def mark_seat_booked(sender, instance, created, **kwargs):
    if created:  # Only update if it's a new booking
        seat = instance.seat
        seat.is_booked = True
        seat.save()

# Signal to mark seat as available when a booking is deleted
@receiver(post_delete, sender=Booking)
def mark_seat_available(sender, instance, **kwargs):
    seat = instance.seat
    seat.is_booked = False
    seat.save()
