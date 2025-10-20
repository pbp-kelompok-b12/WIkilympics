from django.forms import ModelForm
from sports.models import Sports

class SportsForm(ModelForm):
    class Meta:
        model = Sports
        fields = [
                    "sport_name", 
                    "sport_img", 
                    "sport_description", 
                    "participation_structure", 
                    "sport_type",
                    "country_of_origin",
                    "country_flag_img",
                    "first_year_played",
                    "history_description",
                    "equipment"
                ]