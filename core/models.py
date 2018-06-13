from datetime import datetime 

from django.contrib.auth.models import User
from django.db import models
import pytz

class Thread(models.Model):
    title = models.CharField(max_length=256)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)


class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    time_posted = models.DateTimeField(default=datetime.now)

