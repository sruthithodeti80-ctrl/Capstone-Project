"""
Sample Data Seeder for CinePrime Movie Booking Portal
Run: python seed_data.py
"""
import os
import sys
import django
from datetime import date, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviebooking.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from movies.models import Movie, Showtime, SeatBooking, MovieReview

def run():
    print("🎬 Seeding CinePrime database...")

    movies_data = [
        {
            "title": "Avengers: Endgame",
            "description": "After the devastating events of Avengers: Infinity War, the universe is in ruins. With the help of remaining allies, the Avengers assemble once more in order to reverse Thanos' actions and restore balance to the universe.",
            "genre": "Action, Sci-Fi, Adventure",
            "duration_minutes": 181,
            "release_date": date(2019, 4, 26),
            "poster_url": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg",
            "banner_url": "https://image.tmdb.org/t/p/original/7RyHsO4yDXtBv1zUU3mTpHeQ0d5.jpg",
            "rating_class": "PG-13",
            "is_now_showing": True,
        },
        {
            "title": "Interstellar",
            "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival as Earth faces devastating climate change.",
            "genre": "Sci-Fi, Drama, Adventure",
            "duration_minutes": 169,
            "release_date": date(2014, 11, 7),
            "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
            "banner_url": "https://image.tmdb.org/t/p/original/pbrkL804c8yAv3zBZR4QPEafpAR.jpg",
            "rating_class": "PG-13",
            "is_now_showing": True,
        },
        {
            "title": "The Batman",
            "description": "When a sadistic serial killer begins murdering key political figures in Gotham, Batman is forced to investigate the city's hidden corruption and question his family's involvement.",
            "genre": "Action, Crime, Mystery",
            "duration_minutes": 176,
            "release_date": date(2022, 3, 4),
            "poster_url": "https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg",
            "banner_url": "https://image.tmdb.org/t/p/original/b0PlSFdDwbyK0cf5RxwDpaOJQvQ.jpg",
            "rating_class": "PG-13",
            "is_now_showing": True,
        },
        {
            "title": "Joker",
            "description": "A failed stand-up comedian turns to a life of crime and chaos in Gotham City while slowly descending into madness and becoming the iconic villain: The Joker.",
            "genre": "Crime, Drama, Thriller",
            "duration_minutes": 122,
            "release_date": date(2019, 10, 4),
            "poster_url": "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg",
            "banner_url": "https://image.tmdb.org/t/p/original/n6bUvigpRFqSwmPp1m2YADwSx5L.jpg",
            "rating_class": "R",
            "is_now_showing": False,
        },
        {
            "title": "Dune: Part Two",
            "description": "Paul Atreides unites with Chani and the Fremen while on a path of revenge against the conspirators who destroyed his family. Facing a choice between the love of his life and the fate of the universe, he endeavors to prevent a terrible future only he can foresee.",
            "genre": "Sci-Fi, Action, Adventure",
            "duration_minutes": 166,
            "release_date": date(2024, 3, 1),
            "poster_url": "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
            "banner_url": "https://image.tmdb.org/t/p/original/xOMo8BRK7PfcJv9JCnx7s5hj0PX.jpg",
            "rating_class": "PG-13",
            "is_now_showing": True,
        },
    ]

    created_movies = []
    for data in movies_data:
        movie, created = Movie.objects.get_or_create(
            title=data['title'],
            defaults=data
        )
        created_movies.append(movie)
        status = "✅ Created" if created else "⏭ Exists"
        print(f"  {status}: {movie.title}")

    # Create Showtimes (starting from today, future dates)
    print("\n🕐 Creating showtimes...")
    screens = ["Screen 1", "Screen 2", "IMAX", "Dolby ATMOS", "Screen 3"]
    times = [10, 13, 16, 19, 22]  # Hours

    for i, movie in enumerate(created_movies):
        if movie.is_now_showing:
            for j in range(3):  # 3 showtimes per movie
                show_time = timezone.now() + timedelta(days=j, hours=times[j % len(times)])
                showtime, created = Showtime.objects.get_or_create(
                    movie=movie,
                    screen=screens[i % len(screens)],
                    start_time=show_time,
                    defaults={'ticket_price': 12.00}
                )
                status = "✅ Created" if created else "⏭ Exists"
                print(f"  {status}: {showtime}")

    # Sample Reviews
    print("\n⭐ Creating sample reviews...")
    reviews_data = [
        ("Avengers: Endgame", "Alex Chen", 5, "An absolutely epic conclusion to 11 years of Marvel storytelling! The emotional payoff was incredible."),
        ("Avengers: Endgame", "Sarah Johnson", 4, "Fantastic film with an emotional finale. A few pacing issues in the middle act but overall outstanding!"),
        ("Interstellar", "Dr. Mike Ross", 5, "Nolan's masterpiece. The science is compelling and the emotional depth is extraordinary."),
        ("Interstellar", "Emma Watson Fan", 4, "Mind-bending and beautiful. The sound mixing was a bit overwhelming but the visuals and story are stunning."),
        ("The Batman", "RatedR_Reviews", 5, "The best Batman film ever made. Pattinson is a revelation in this dark, atmospheric noir detective story."),
        ("Joker", "CinematicUniverse", 5, "Joaquin Phoenix delivered a once-in-a-generation performance. A haunting and challenging masterpiece."),
        ("Dune: Part Two", "SciFiGeek", 5, "Villeneuve has created something truly epic. Every frame is a work of art. Zendaya and Chalamet are magnetic."),
        ("Dune: Part Two", "FilmCritic2024", 4, "Stunning visual spectacle with incredible world-building. Some character development felt rushed but overall breathtaking."),
    ]

    for movie_title, reviewer, rating, comment in reviews_data:
        try:
            movie = Movie.objects.get(title=movie_title)
            review, created = MovieReview.objects.get_or_create(
                movie=movie,
                reviewer_name=reviewer,
                defaults={'rating': rating, 'comment': comment}
            )
            status = "✅ Created" if created else "⏭ Exists"
            print(f"  {status}: Review by {reviewer} on {movie_title}")
        except Movie.DoesNotExist:
            print(f"  ⚠ Movie '{movie_title}' not found, skipping review.")

    print("\n🎉 Database seeded successfully! CinePrime is ready to launch.")

if __name__ == '__main__':
    run()
