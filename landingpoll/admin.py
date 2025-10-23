from django.contrib import admin
from .models import PollQuestion, PollOption


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 1  


@admin.register(PollQuestion)
class PollQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'created_at', 'total_votes')
    search_fields = ('question_text',)
    inlines = [PollOptionInline]


@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'option_text', 'votes')
