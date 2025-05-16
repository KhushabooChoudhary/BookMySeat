from django.shortcuts import render, redirect ,get_object_or_404
from .models import Movie,Theater,Seat,Booking,UserPreference
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from datetime import datetime
from django.core.paginator import Paginator 
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.db.models import Count
import razorpay
from django.urls import reverse
from django.db import IntegrityError, transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync









def movie_list(request):
    movies = Movie.objects.all()

    # Filter movies by genre and language
    genre_filter = request.GET.get('genre')
    language_filter = request.GET.get('language')

    if genre_filter:
        movies = movies.filter(genre=genre_filter)
    if language_filter:
        movies = movies.filter(language=language_filter)

    paginator = Paginator(movies, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'movies/movie_list.html', {
        'page_obj': page_obj,
        'genres': Movie.GENRE_CHOICES,
        'languages': Movie.LANGUAGE_CHOICES,
    })

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movies/movie_detail.html', {'movie': movie})

# def theater_list(request,movie_id):
#     movie = get_object_or_404(Movie,id=movie_id)
#     theater=Theater.objects.filter(movie=movie)
#     return render(request,'movies/theater_list.html',{'movie':movie,'theaters':theater})

def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)

    # Prepare theater data with available seats
    theater_info = []
    for theater in theaters:
        available_seats = Seat.objects.filter(theater=theater, is_booked=False).count()
        status = "Seats Available" if available_seats > 0 else "Fully Booked"

        theater_info.append({
            "theater": theater,  # Pass the entire theater object
            "available_seats": available_seats,
            "status": status
        })

    return render(request, 'movies/theater_list.html', {
        'movie': movie,
        'theater_info': theater_info  # Ensure this variable is passed
    })


@login_required(login_url='/login/')




def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)

    if request.method == 'POST':
        print("🔹 POST Data:", request.POST)
        selected_seats = request.POST.getlist('seats')
        print("✅ Selected Seats:", selected_seats)

        if not selected_seats:
            messages.error(request, "❌ No seat selected. Please select at least one seat.")
            return redirect('book_seats', theater_id=theater.id)

        error_seats = []
        total_price = 0
        booked_seats = []
        created_bookings = []

        for seat_id in selected_seats:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue

            try:
                booking = Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    movie=theater.movie,
                    theater=theater
                )
                seat.is_booked = True
                seat.save()
                booked_seats.append(seat.seat_number)
                total_price += float(seat.calculate_dynamic_price())
                created_bookings.append(booking)

            except IntegrityError:
                error_seats.append(seat.seat_number)

        if error_seats:
            messages.error(request, f"❗ The following seats are already booked: {', '.join(error_seats)}")
            return redirect('book_seats', theater_id=theater.id)

        if not created_bookings:
            messages.error(request, "❌ Error: Booking not created. Please select a seat.")
            return redirect('book_seats', theater_id=theater.id)

        # ✅ Broadcast seat update via WebSockets
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"theater_{theater.id}",  # Group name based on theater ID
            {
                "type": "seat_update",
                "seat_numbers": booked_seats,
                "action": "booked",
            }
        )

        primary_booking = created_bookings[0] if created_bookings else None
        if primary_booking is None:
            messages.error(request, "⚠️ No booking ID found. Booking failed.")
            return redirect('book_seats', theater_id=theater.id)

        print(f"Primary Booking ID: {primary_booking.id}")

        # ✅ Initialize Razorpay client
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            order_amount = int(total_price * 100)  # Convert to paisa
            order_currency = "INR"
            order = razorpay_client.order.create({
                "amount": order_amount,
                "currency": order_currency,
                "payment_capture": "1"
            })

            primary_booking.razorpay_payment_id = order["id"]
            primary_booking.save()

            print(f"Razorpay Order ID: {order['id']} for Booking ID: {primary_booking.id}")

            return redirect("razorpay_checkout", booking_id=primary_booking.id)

        except razorpay.errors.BadRequestError as e:
            messages.error(request, f"❌ Razorpay Error: {str(e)}")
            return redirect("book_seats", theater_id=theater.id)

    return render(request, 'movies/seat_selection.html', {
        'theater': theater,
        'seats': seats
    })

def send_booking_confirmation_email(user, theater, seats, total_price):
    subject = "Your Movie Booking Confirmation"
    message = f"""
    Dear {user.username},

    Your booking is confirmed for {theater.movie.name}.
    Theater: {theater.name}
    Location: {theater.location}
    Show Time: {theater.time}
    
    Seats: {', '.join(seats)}
    Total Price: ₹{total_price}

    Thank you for choosing BookMySeat!
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False  # Ensure this is set to False for error visibility
    )

from django.http import HttpResponse

def test_email(request):
    try:
        send_mail(
            'Test Email - BookMyShow',
            'This is a test email to confirm the email configuration.',
            settings.DEFAULT_FROM_EMAIL,
            ['your_test_email@gmail.com'],
            fail_silently=False
        )
        return HttpResponse("✅ Test email sent successfully.")
    except Exception as e:
        return HttpResponse(f"❌ Error sending test email: {e}")



# to highlight todays show
def recommend_movies(user):
    """Recommendation logic based on user preferences or popular movies"""
    
    # If the user is authenticated, recommend based on their preferences
    if user.is_authenticated:
        preferences = UserPreference.objects.filter(user=user).first()
        preferred_genres = preferences.preferred_genres.split(',') if preferences else []

        recommended_movies = Movie.objects.filter(
            genre__in=preferred_genres
        ).order_by('-rating')[:5]

    else:
        # For guests, recommend popular movies based on bookings
        recommended_movies = Movie.objects.annotate(
            booking_count=Count('booking')
        ).order_by('-booking_count', '-release_date')[:5]

    return recommended_movies

def home(request):
    current_datetime = datetime.now()
    
    # Get all movies
    movies = Movie.objects.all()

    # Recommended Movies Logic
    if request.user.is_authenticated:
        user_bookings = Booking.objects.filter(user=request.user)
        booked_movie_ids = user_bookings.values_list('movie_id', flat=True)
        recommended_movies = Movie.objects.filter(id__in=booked_movie_ids)
    else:
        recommended_movies = movies.order_by('-release_date')[:4]  # Default to latest movies

    # Get today's shows (filter by today's date)
    todays_shows = Theater.objects.filter(time__date=current_datetime.date())

    context = {
        'todays_shows': todays_shows,
        'movies': movies,
        'recommended_movies': recommended_movies,
        'current_date': current_datetime.date(),
    }

    return render(request, 'home.html', context)


@login_required
def razorpay_checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # ✅ Fetch correct dynamic price
    total_price = float(booking.seat.calculate_dynamic_price())  # Ensure correct price
    total_price_paisa = int(total_price * 100)  # Convert to paisa

    # ✅ Initialize Razorpay Client
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # ✅ Create Razorpay Order
    order = razorpay_client.order.create({
        "amount": total_price_paisa,
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "booking": booking,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": order["id"],
        "amount": total_price  # Keep in rupees for frontend display
    }

    return render(request, "movies/razorpay_checkout.html", context)

@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # ✅ Send confirmation email after successful payment
    send_booking_confirmation_email(request.user, booking.theater, [booking.seat.seat_number], booking.seat.price)

    messages.success(request, f"✅ Payment Successful! Your booking for {booking.movie.name} is confirmed.")
    return redirect('profile')

from django.http import JsonResponse

def create_razorpay_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        total_price = int(data.get("total_price", 0) * 100)  # Convert to paisa
        seats = data.get("seats", [])

        if not seats or total_price <= 0:
            return JsonResponse({"success": False, "error": "Invalid data"})

        # ✅ Initialize Razorpay Client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            # ✅ Create Razorpay Order
            order = client.order.create({
                "amount": total_price,
                "currency": "INR",
                "payment_capture": "1"
            })

            return JsonResponse({
                "success": True,
                "order_id": order["id"],
                "amount": order["amount"]
            })

        except razorpay.errors.BadRequestError as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})