import uuid
from django.db import models
from django.contrib.auth.models import User

class Forum(models.Model):
    name = models.ForeignKey(User, on_delete=models.RESTRICT, null=True)
    topic= models.CharField(max_length=300)
    description = models.CharField(max_length=1000,blank=True)
    date_created=models.DateTimeField(auto_now_add=True,null=True)
    thumbnail = models.URLField(blank=True, null = False)
    
    def __str__(self):
        return str(self.topic)
 
class Discussion(models.Model):
    username = models.ForeignKey(User, on_delete=models.RESTRICT, null=True)
    forum = models.ForeignKey(Forum,blank=True,on_delete=models.CASCADE)
    discuss = models.CharField(max_length=1000)
    date_created=models.DateTimeField(auto_now_add=True,null=True)

 
    def __str__(self):
        return str(self.forum)
#