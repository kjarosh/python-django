from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.db.models.aggregates import Max
from django.utils import timezone
import pytz


class Section(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()


class ThreadManager(models.Manager):

    def active_threads(self, thread_from, thread_to, section=None):
        """
        Get active threads, sorted by date. Returned format:
        
        ┌──────────────┬───────────┬──────────────────────────┬───────────────┐
        │    title     │    id     │          author          │   activity    │
        ├──────────────┼───────────┼──────────────────────────┼───────────────┤
        │ thread title │ thread id │ thread creator user name │ activity date │
        └──────────────┴───────────┴──────────────────────────┴───────────────┘
        
        @param thread_from: # of thread to start form
        @param thread_to: # of thread to end at
        @param section: section to get threads from,
                        or None to get threads from all sections
        
        @return: a pair (threads, more); threads is a list of threads
                 and more is True when more threads are available after thread_to
        """
        
        threads = Post.objects
        
        if section:
            threads = threads.filter(thread__section=section)
        
        threads = threads \
            .values('thread__id', 'thread__title', 'thread__creator__username') \
            .annotate(last_date=Max('time_posted')) \
            .order_by('-last_date')[thread_from:thread_to + 1]
        
        more = (len(threads) == thread_to - thread_from + 1)
        threads = threads[0:thread_to - thread_from]
        
        return [ {
            'title': thread['thread__title'],
            'id': thread['thread__id'],
            'author': thread['thread__creator__username'],
            'activity': thread['last_date']
        } for thread in threads ], more


class Thread(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=256)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    
    objects = ThreadManager()


class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    time_posted = models.DateTimeField(default=timezone.now)


admin.site.register(Section)

