from django.db import models
import uuid

class Athletes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    athlete_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    sport = models.CharField(max_length=100)
    biography = models.TextField()
    athlete_photo = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.athlete_name

    def get_sport_display(self):
        return self.sport