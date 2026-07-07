import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.CharField(max_length=100, help_text="Comma-separated genres, e.g., Action, Sci-Fi")
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")
    release_date = models.DateField()
    poster_url = models.URLField(max_length=500, help_text="URL to movie poster image")
    banner_url = models.URLField(max_length=500, help_text="URL to wide movie banner image", blank=True, null=True)
    rating_class = models.CharField(max_length=10, help_text="Classification, e.g., PG-13, R, U/A")
    is_now_showing = models.BooleanField(default=True)

    class Meta:
        ordering = ['-release_date']

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            return round(avg, 1) if avg is not None else 0.0
        return 0.0

    @property
    def genre_list(self):
        return [g.strip() for g in self.genre.split(',') if g.strip()]


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    start_time = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=6, decimal_places=2, default=12.00)
    screen = models.CharField(max_length=50, help_text="e.g., Screen 1, IMAX, Dolby Cinema")

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        local_time = timezone.localtime(self.start_time)
        return f"{self.movie.title} - {self.screen} @ {local_time.strftime('%b %d, %I:%M %p')}"

    @property
    def is_past(self):
        return self.start_time < timezone.now()


class SeatBooking(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='bookings')
    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    seats = models.CharField(max_length=255, help_text="Comma-separated seat codes, e.g., A1, A2")
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    booking_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booking_time']

    def __str__(self):
        return f"Booking {self.booking_id} - {self.customer_name} ({self.showtime.movie.title})"

    def get_seat_list(self):
        return [s.strip().upper() for s in self.seats.split(',') if s.strip()]

    def clean(self):
        super().clean()
        try:
            showtime = self.showtime
        except Exception:
            return  # showtime not assigned yet, skip validation
        if showtime and self.seats:
            requested_seats = self.get_seat_list()
            
            # Find all other bookings for this showtime
            other_bookings = SeatBooking.objects.filter(showtime=self.showtime)
            if self.pk:
                other_bookings = other_bookings.exclude(pk=self.pk)
            
            # Extract all booked seats for this showtime
            booked_seats = []
            for booking in other_bookings:
                booked_seats.extend(booking.get_seat_list())
                
            # Intersect to find duplicates
            duplicate_seats = set(requested_seats).intersection(set(booked_seats))
            if duplicate_seats:
                raise ValidationError({
                    'seats': f"The following seats are already booked: {', '.join(sorted(duplicate_seats))}"
                })

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"MTB{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class MovieReview(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 and 5 stars"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.reviewer_name} on {self.movie.title} ({self.rating} stars)"
