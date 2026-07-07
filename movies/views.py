import json
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.db import transaction
from django.db.models import Q, Avg
from django.contrib import messages
from django.utils import timezone
from .models import Movie, Showtime, SeatBooking, MovieReview
from .forms import SeatBookingForm, MovieReviewForm

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)


class HomeView(TemplateView):
    template_name = 'movies/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Now Showing movies
        context['now_showing'] = Movie.objects.filter(is_now_showing=True)[:6]
        
        # Popular movies ordered by average rating
        context['popular_movies'] = Movie.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:6]
        
        # Recently added movies
        context['recent_movies'] = Movie.objects.order_by('-release_date')[:6]
        
        # Latest Reviews
        context['latest_reviews'] = MovieReview.objects.select_related('movie').order_by('-created_at')[:4]
        return context


class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 6

    def get_queryset(self):
        queryset = Movie.objects.all()
        q = self.request.GET.get('q')
        genre = self.request.GET.get('genre')
        showing = self.request.GET.get('showing')
        
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | 
                Q(description__icontains=q) | 
                Q(genre__icontains=q)
            )
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        if showing == 'now':
            queryset = queryset.filter(is_now_showing=True)
        elif showing == 'upcoming':
            queryset = queryset.filter(is_now_showing=False)
            
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Extract unique list of genres
        all_genres = set()
        for movie in Movie.objects.all():
            for g in movie.genre_list:
                all_genres.add(g)
        
        context['genres'] = sorted(list(all_genres))
        context['selected_genre'] = self.request.GET.get('genre', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_showing'] = self.request.GET.get('showing', '')
        return context


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch showtimes starting from now/today onwards
        context['showtimes'] = self.object.showtimes.filter(
            start_time__gte=timezone.now()
        ).order_by('start_time')
        context['review_form'] = MovieReviewForm()
        context['reviews'] = self.object.reviews.all().order_by('-created_at')
        return context


class ReviewCreateView(CreateView):
    model = MovieReview
    form_class = MovieReviewForm
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        movie_id = self.kwargs.get('movie_id')
        movie = get_object_or_404(Movie, pk=movie_id)
        form = self.get_form()
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.save()
            messages.success(request, "Your review has been submitted successfully!")
        else:
            messages.error(request, "Failed to submit review. Please check your inputs.")
        return redirect('movie_detail', pk=movie.pk)


class SeatBookingCreateView(CreateView):
    model = SeatBooking
    form_class = SeatBookingForm
    template_name = 'movies/booking.html'

    def get_showtime(self):
        return get_object_or_404(Showtime, pk=self.kwargs.get('showtime_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        showtime = self.get_showtime()
        context['showtime'] = showtime
        
        # Get all seats already booked for this showtime
        booked_bookings = SeatBooking.objects.filter(showtime=showtime)
        booked_seats = []
        for booking in booked_bookings:
            booked_seats.extend(booking.get_seat_list())
            
        context['booked_seats'] = json.dumps(booked_seats)
        return context

    def form_valid(self, form):
        showtime = self.get_showtime()
        booking = form.save(commit=False)
        booking.showtime = showtime
        
        try:
            with transaction.atomic():
                # Lock the Showtime row for update during execution
                locked_showtime = Showtime.objects.select_for_update().get(pk=showtime.pk)
                
                # Fetch all current bookings for this showtime
                requested_seats = booking.get_seat_list()
                other_bookings = SeatBooking.objects.filter(showtime=locked_showtime)
                booked_seats = []
                for b in other_bookings:
                    booked_seats.extend(b.get_seat_list())
                
                # Validate duplicate seat bookings
                duplicate_seats = set(requested_seats).intersection(set(booked_seats))
                if duplicate_seats:
                    form.add_error('seats', f"The following seats are already booked: {', '.join(sorted(duplicate_seats))}")
                    return self.form_invalid(form)
                
                # Price calculation
                booking.total_price = len(requested_seats) * locked_showtime.ticket_price
                booking.save()
                
                return redirect('booking_success', booking_id=booking.booking_id)
                
        except Exception as e:
            form.add_error(None, f"Transaction error occurred: {str(e)}")
            return self.form_invalid(form)


class BookingSuccessView(TemplateView):
    template_name = 'movies/booking_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.kwargs.get('booking_id')
        if booking_id:
            booking = get_object_or_404(
                SeatBooking.objects.select_related('showtime__movie', 'showtime'), 
                booking_id=booking_id
            )
            context['booking'] = booking
        else:
            context['error'] = "No booking ID provided."
        return context
