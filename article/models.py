import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Article(models.Model):
    CATEGORY_CHOICES = [
        ('athletics', 'Athletics'),
        ('swimming', 'Swimming'),
        ('b', 'B'),
        ('a', 'A'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField()
    content = models.TextField()
    category = models.CharField(choices=CATEGORY_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    thumbnail = models.URLField(blank=False, null=False)

    # Mendetect user like dislike
    like_user = models.ManyToManyField(User, related_name="liked_articles", blank=True)
    dislike_user = models.ManyToManyField(User, related_name="disliked_articles", blank=True)

    def __str__(self):
        return self.title
    
    @property
    def is_trending(self):
        return self.like_user.count() > 6
    
    @property
    def like_count(self):
        return self.like_user.count()

        