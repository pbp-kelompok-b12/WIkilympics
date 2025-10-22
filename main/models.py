import uuid
from django.db import models

class GeeksModel(models.Model):

    # fields of the model
    title = models.CharField(max_length = 200)
    description = models.TextField()

    # renames the instances of the model
    # with their title name
    def __str__(self):
        return self.title

class forum(models.Model):
    name=models.CharField(max_length=200,default="anonymous" )
    email=models.CharField(max_length=200,null=True)
    topic= models.CharField(max_length=300)
    description = models.CharField(max_length=1000,blank=True)
    link = models.CharField(max_length=100 ,null =True)
    date_created=models.DateTimeField(auto_now_add=True,null=True)
    
    def __str__(self):
        return str(self.topic)
 
#child model
class Discussion(models.Model):
    forum = models.ForeignKey(forum,blank=True,on_delete=models.CASCADE)
    discuss = models.CharField(max_length=1000)
 
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