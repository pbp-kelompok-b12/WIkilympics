from django.db import models
import uuid

class Athletes(models.Model):
    SPORT_CHOICES = [
        ('swimming', 'Swimming'),
        ('athletics', 'Athletics'),
        ('gymnastics', 'Gymnastics'),
        ('basketball', 'Basketball'),
        ('football', 'Football'),
        ('tennis', 'Tennis'),
        ('boxing', 'Boxing'),
        ('weightlifting', 'Weightlifting'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    athlete_name = models.CharField(max_length=255)
    athlete_photo = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=100)
    country_flag = models.URLField(blank=True, null=True)
    sport = models.CharField(max_length=50, choices=SPORT_CHOICES)
    biography = models.TextField()
    date_of_birth = models.DateField(blank=True, null=True)
    height = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    achievements = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.athlete_name