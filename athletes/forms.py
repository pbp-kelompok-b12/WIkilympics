from django import forms
from athletes.models import Athletes

class AthletesForm(forms.ModelForm):
    class Meta:
        model = Athletes
        fields = [
            'athlete_name', 
            'athlete_photo', 
            'country', 
            'country_flag', 
            'sport', 
            'biography',
            'date_of_birth',
            'height',
            'weight',
            'achievements'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'biography': forms.Textarea(attrs={'rows': 4}),
            'achievements': forms.Textarea(attrs={'rows': 3}),
        }