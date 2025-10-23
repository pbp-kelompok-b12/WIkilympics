from django import forms
from .models import PollQuestion

class PollForm(forms.ModelForm):
    class Meta:
        model = PollQuestion
        fields = ['question_text', 'option1', 'option2']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan pertanyaan'}),
            'option1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pilihan pertama'}),
            'option2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pilihan kedua'}),
        }
