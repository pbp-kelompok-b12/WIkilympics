from django.forms import ModelForm
from django import forms
from .models import *
 
class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = ['topic', 'description', 'thumbnail']
        widgets = {
            'topic': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-md focus:ring-2 focus:ring-[#FFC107] focus:border-[#2B4C9F] transition text-gray-800'
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-md focus:ring-2 focus:ring-[#FFC107] focus:border-[#2B4C9F] transition text-gray-800'
            }),
            'thumbnail': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-md focus:ring-2 focus:ring-[#FFC107] focus:border-[#2B4C9F] transition text-gray-800'
            }),
        }
class DiscussionForm(ModelForm):
    class Meta:
        model = Discussion
        fields = ['discuss']
        widgets = {
            'discuss': forms.Textarea(attrs={
                'rows': 6,
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-md focus:ring-2 focus:ring-[#FFC107] focus:border-[#2B4C9F] transition text-gray-800'
            }),
        }
        labels = {
            'discuss': 'Description'
        }