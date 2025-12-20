import uuid
from django.db import models

# Create your models here.
class Sports(models.Model):
    PARTICIPATION_STRUCTURE = [
        ('individual', 'Individual'),
        ('team', 'Team'),
        ('both', 'Individual & Team')
    ]

    SPORT_TYPE = [
        ('water_sport', 'Water Sport'),
        ('strength_sport', 'Strength Sport'),
        ('athletic_sport', 'Athletic Sport'),
        ('racket_sport', 'Racket Sport'),
        ('ball_sport', 'Ball Sport'),
        ('combat_sport', 'Combat Sport'),
        ('target_sport', 'Target Sport'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sport_name = models.CharField(max_length=255)
    sport_img = models.URLField( max_length = 2048, blank=True, null=True)
    sport_description = models.TextField()
    participation_structure = models.CharField(max_length=20, choices=PARTICIPATION_STRUCTURE, default='individual')
    sport_type = models.CharField(max_length=20, choices=SPORT_TYPE, default='athletic_sport')
    country_of_origin = models.CharField(max_length=255)
    country_flag_img = models.URLField(max_length=5096 , blank=True, null=True)
    first_year_played = models.IntegerField(default=0)
    history_description = models.TextField()
    equipment = models.TextField()
    
    def __str__(self):
       return self.sport_name
    