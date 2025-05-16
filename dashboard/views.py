from django.db.models import Count, Sum
from django.shortcuts import render
from movies.models import Booking, Movie, Theater

def admin_dashboard(request):
    # Total Revenue Calculation
    total_revenue = Booking.objects.aggregate(total=Sum('seat__price'))['total'] or 0

    # Most Popular Movie (Corrected)
    most_popular_movie = (
        Movie.objects.annotate(total_bookings=Count('booking'))
        .order_by('-total_bookings')
        .first()
    )

    # Busiest Theater (Corrected)
    busiest_theater = (
        Theater.objects.annotate(total_bookings=Count('booking'))
        .order_by('-total_bookings')
        .first()
    )

    # Most Popular Movies (for chart)
    popular_movies = (
        Movie.objects.annotate(total_bookings=Count('booking'))
        .order_by('-total_bookings')[:5]
    )

    # Busiest Theaters (for chart)
    busy_theaters = (
        Theater.objects.annotate(total_bookings=Count('booking'))
        .order_by('-total_bookings')[:5]
    )

    context = {
        'total_revenue': total_revenue,
        'most_popular_movie': most_popular_movie,
        'busiest_theater': busiest_theater,
        'popular_movies': popular_movies,
        'busy_theaters': busy_theaters,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)
