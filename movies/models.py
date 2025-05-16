from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
from decimal import Decimal
import datetime





class Movie(models.Model):
    GENRE_CHOICES = [
        ('Action', 'Action'),
        ('Comedy', 'Comedy'),
        ('Drama', 'Drama'),
        ('Horror', 'Horror'),
        ('Sci-Fi', 'Sci-Fi'),
    ]
    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('Hindi', 'Hindi'),
        ('Spanish', 'Spanish'),
        ('French', 'French'),
    ]
    genre = models.CharField(max_length=20,choices=GENRE_CHOICES,default='Action')
    language = models.CharField(max_length=20,choices=LANGUAGE_CHOICES,default='Hindi')
    name= models.CharField(max_length=255)
    image= models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3,decimal_places=1)
    trailer_url = models.URLField(blank=True, null=True)
    cast= models.TextField()
    description= models.TextField(blank=True,null=True) # optional
    release_date = models.DateField(default=datetime.date.today)


    def __str__(self):
        return self.name

class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='theaters')
    time= models.DateTimeField()
    location = models.CharField(max_length=255, null=True, blank=True)  # Add location here


    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'

class Seat(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=150.00)  # Add price
    show_time = models.DateTimeField(default=timezone.now) 

    def calculate_dynamic_price(self):
        show_time = self.theater.time
        remaining_seats = Seat.objects.filter(theater=self.theater, is_booked=False).count()

        # Calculate time difference in hours
        time_to_show = (show_time - timezone.now()).total_seconds() / 3600  

        # Pricing logic
        if time_to_show <= 24:
            if remaining_seats <= 5:
                return round(self.price * Decimal(1.7), 2)
            elif remaining_seats <= 10:
                return round(self.price * Decimal(1.4), 2)
            else:
                return round(self.price * Decimal(1.2), 2)

        elif time_to_show <= 72:
            if remaining_seats <= 5:
                return round(self.price * Decimal(1.4), 2)
            elif remaining_seats <= 10:
                return round(self.price * Decimal(1.2), 2)
            else:
                return self.price

        return self.price

    def __str__(self):
        return f'{self.seat_number} in {self.theater.name}'

class Booking(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    seat=models.OneToOneField(Seat,on_delete=models.CASCADE)
    movie=models.ForeignKey(Movie,on_delete=models.CASCADE)
    theater=models.ForeignKey(Theater,on_delete=models.CASCADE)
    booked_at=models.DateTimeField(auto_now_add=True)
    show_date = models.DateField(default=timezone.now)  
    payment_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Paid", "Paid"), ("Failed", "Failed")],
        default="Pending",
    )
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Booking by{self.user.username} for {self.seat.seat_number} at {self.theater.name} - {self.payment_status}'



# recommondation model
class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_genres = models.CharField(max_length=200)