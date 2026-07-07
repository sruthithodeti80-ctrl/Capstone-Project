from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('movies/', views.MovieListView.as_view(), name='movie_list'),
    path('movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('movies/<int:movie_id>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    path('book/<int:showtime_id>/', views.SeatBookingCreateView.as_view(), name='seat_booking'),
    path('booking/success/<str:booking_id>/', views.BookingSuccessView.as_view(), name='booking_success'),
]
