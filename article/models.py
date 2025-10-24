import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Article(models.Model):
    CATEGORY_CHOICES = [
        ('athletics', 'Athletics'),
        ('archery', 'Archery'),
        ('artistic_gymnastics', 'Artistic Gymnastics'),
        ('artistic_swimming', 'Artistic Swimming'),
        ('badminton', 'Badminton'),
        ('baseball_softball', 'Baseball/Softball'),
        ('basketball', 'Basketball'),
        ('beach_volleyball', 'Beach Volleyball'),
        ('boxing', 'Boxing'),
        ('canoe_slalom', 'Canoe Slalom'),
        ('cycling_road', 'Cycling Road'),
        ('diving', 'Diving'),
        ('fencing', 'Fencing'),
        ('football', 'Football'),
        ('handball', 'Handball'),
        ('hockey', 'Hockey'),
        ('judo', 'Judo'),
        ('karate', 'Karate'),
        ('marathon_swimming', 'Marathon Swimming'),
        ('rowing', 'Rowing'),
        ('rhythmic_gymnastics', 'Rhythmic Gymnastics'),
        ('sailing', 'Sailing'),
        ('shooting', 'Shooting'),
        ('swimming', 'Swimming'),
        ('table_tennis', 'Table Tennis'),
        ('taekwondo', 'Taekwondo'),
        ('trampoline_gymnastics', 'Trampoline Gymnastics'),
        ('triathlon', 'Triathlon'),
        ('water_polo', 'Water Polo'),
        ('weightlifting', 'Weightlifting'),
        ('wrestling', 'Wrestling'),
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
    