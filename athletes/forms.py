from django import forms
from athletes.models import Athletes

class AthletesForm(forms.ModelForm):
    class Meta:
        model = Athletes
        fields = ['athlete_name', 'country', 'sport', 'biography', 'athlete_photo']
        widgets = {
            'biography': forms.Textarea(attrs={'rows': 4}),
        }