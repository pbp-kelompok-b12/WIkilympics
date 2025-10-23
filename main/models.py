import uuid
from django.db import models
from django.contrib.auth.models import User

class Forum(models.Model):
    name = models.ForeignKey(User, on_delete=models.RESTRICT, null=True)
    topic= models.CharField(max_length=300)
    description = models.CharField(max_length=1000,blank=True)
    date_created=models.DateTimeField(auto_now_add=True,null=True)
    
    def __str__(self):
        return str(self.topic)
 
#child model
class Discussion(models.Model):
    username = models.ForeignKey(User, on_delete=models.RESTRICT, null=True)
    forum = models.ForeignKey(Forum,blank=True,on_delete=models.CASCADE)
    discuss = models.CharField(max_length=1000)
    date_created=models.DateTimeField(auto_now_add=True,null=True)

 
    def __str__(self):
        return str(self.forum)
# class News(models.Model):
#     CATEGORY_CHOICES = [
#         ('transfer', 'Transfer'),
#         ('update', 'Update'),
#         ('exclusive', 'Exclusive'),
#         ('match', 'Match'),
#         ('rumor', 'Rumor'),
#         ('analysis', 'Analysis'),
#     ]
    
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='update')
#     thumbnail = models.URLField(blank=True, null=True)
#     news_views = models.PositiveIntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_featured = models.BooleanField(default=False)
    
#     def __str__(self):
#         return self.title
    
#     @property
#     def is_news_hot(self):
#         return self.news_views > 20
        
#     def increment_views(self):
#         self.news_views += 1
#         self.save()