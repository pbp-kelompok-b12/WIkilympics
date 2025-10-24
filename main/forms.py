from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'organizer', 'date', 'location', 'sport_branch', 'image_url', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tulis deskripsi kegiatan di sini...'})
        }