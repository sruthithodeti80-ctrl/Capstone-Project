from django import forms
from .models import SeatBooking, MovieReview

class SeatBookingForm(forms.ModelForm):
    class Meta:
        model = SeatBooking
        fields = ['customer_name', 'customer_email', 'customer_phone', 'seats']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control bg-dark border-secondary text-white',
                'placeholder': 'Enter your name',
                'required': 'required'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control bg-dark border-secondary text-white',
                'placeholder': 'Enter your email',
                'required': 'required'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control bg-dark border-secondary text-white',
                'placeholder': 'Enter your phone number',
                'required': 'required'
            }),
            'seats': forms.TextInput(attrs={
                'class': 'form-control bg-dark border-secondary text-white readonly-seats',
                'placeholder': 'Select seats from the grid',
                'readonly': 'readonly',
                'required': 'required'
            })
        }

    def clean_seats(self):
        seats_str = self.cleaned_data.get('seats')
        if not seats_str or not seats_str.strip():
            raise forms.ValidationError("You must select at least one seat.")
        return seats_str


class MovieReviewForm(forms.ModelForm):
    class Meta:
        model = MovieReview
        fields = ['reviewer_name', 'rating', 'comment']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={
                'class': 'form-control bg-dark border-secondary text-white',
                'placeholder': 'Enter your name',
                'required': 'required'
            }),
            'rating': forms.HiddenInput(attrs={
                'id': 'id_rating_value',
                'required': 'required'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control bg-dark border-secondary text-white',
                'rows': 4,
                'placeholder': 'Share your cinematic experience...',
                'required': 'required'
            })
        }
