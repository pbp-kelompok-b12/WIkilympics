from django import forms
from .models import PollQuestion

class PollForm(forms.ModelForm):
    class Meta:
        model = PollQuestion
        fields = ['question_text']
        widgets = {
            'question_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan pertanyaan'
            }),
        }
