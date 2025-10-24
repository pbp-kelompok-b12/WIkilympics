from django.db import models

# Create your models here.
class UpcomingEvent(models.Model):
    name = models.CharField(max_length=100)
    organizer = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=100)
    sport_branch = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.date}"