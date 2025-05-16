from django.urls import path
from . import views
from .views import book_seats, razorpay_checkout, payment_success
from .views import create_razorpay_order


urlpatterns=[
    path('',views.movie_list,name='movie_list'),
    path('<int:movie_id>/theaters',views.theater_list,name='theater_list'),
    path('theater/<int:theater_id>/seats/book/', views.book_seats, name='book_seats'),
    path('seat/<int:theater_id>/book/', views.book_seats, name='book_seats'),
    path('test-email/', views.test_email, name='test_email'),
    path('', views.home, name='home'),

    path("razorpay-checkout/<int:booking_id>/", razorpay_checkout, name="razorpay_checkout"),
    path('movies/payment-success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path("razorpay-create-order/", create_razorpay_order, name="create_razorpay_order"),

]

# urlpatterns = [
#     path('', views.movie_list, name='movie_list'),  # List all movies
#     path('<int:movie_id>/theaters/', views.theater_list, name='theater_list'),
#     path('theater/<int:theater_id>/seats/book/', views.book_seats, name='book_seats'),
# ]