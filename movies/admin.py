from django.contrib import admin
from .models import Movie, Showtime, SeatBooking, MovieReview

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'duration_minutes', 'release_date', 'is_now_showing', 'average_rating')
    list_filter = ('is_now_showing', 'release_date')
    search_fields = ('title', 'genre', 'description')
    ordering = ('-release_date',)


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'screen', 'start_time', 'ticket_price')
    list_filter = ('screen', 'start_time', 'movie')
    search_fields = ('movie__title', 'screen')
    ordering = ('start_time',)


@admin.register(SeatBooking)
class SeatBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer_name', 'showtime', 'seats', 'total_price', 'booking_time')
    list_filter = ('showtime__movie', 'booking_time')
    search_fields = ('booking_id', 'customer_name', 'customer_email', 'customer_phone', 'seats')
    ordering = ('-booking_time',)
    readonly_fields = ('booking_id', 'booking_time')


@admin.register(MovieReview)
class MovieReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'reviewer_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'movie')
    search_fields = ('movie__title', 'reviewer_name', 'comment')
    ordering = ('-created_at',)
