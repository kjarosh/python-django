# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import SuspiciousOperation
from django.db import transaction
from django.db.models.aggregates import Max
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, reverse

from core.apps import CoreConfig
from core.models import Thread, Post


def get_active_thread_list(thread_from, thread_to):
    threads = Post.objects \
        .values('thread__id', 'thread__title', 'thread__creator__username') \
        .annotate(last_date=Max('time_posted')) \
        .order_by('-last_date')[thread_from:thread_to]
    
    return [ {
        'title': thread['thread__title'],
        'id': thread['thread__id'],
        'author': thread['thread__creator__username']
    } for thread in threads ]

def index(request):
    context = { 'threads': get_active_thread_list(0, 10) }
    return render(request, 'index.html', context)


def post(request):
    current_user = request.user
    
    if not current_user.is_authenticated:
        return redirect('/accounts/login/?next=' + reverse('post'))
    
    try:
        tid = int(request.POST.get('tid', ''))
    except:
        # post to a new thread
        tid = None
    
    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    if content == '':
        # no content specified
        return render(request, 'post.html', {})
    
    if not tid and title == '':
        # no title specified
        return render(request, 'post.html', {})
    
    if not tid:
        # create a thread if needed
        thread = Thread(title=title, creator=current_user)
        thread.save()
    else:
        thread = Thread.objects.get(id=tid)
    
    post = Post(thread=thread, content=content, author=current_user)
    post.save()
    
    next = request.GET.get('next', '/threads/%d' % thread.id)
    
    return redirect(next)


def threads(request):
    try:
        page = int(request.GET.get('page', '0'))
    except:
        raise Http404
    
    thread_from = page * CoreConfig.threads_per_page
    thread_to = thread_from + CoreConfig.threads_per_page
    
    context = { 'threads': get_active_thread_list(thread_from, thread_to) }
    
    return render(request, 'threads.html', context)


def thread(request, tid):
    try:
        page = int(request.GET.get('page', '0'))
    except:
        raise Http404
    
    try:
        thread = Thread.objects.get(id=tid)
    except ObjectDoesNotExist:
        raise Http404
    
    post_from = page * CoreConfig.posts_per_page
    post_to = post_from + CoreConfig.posts_per_page
    posts = Post.objects \
        .filter(thread=tid) \
        .order_by('time_posted')[post_from:post_to]
    
    if len(posts) == 0:
        raise Http404
    
    context = { 'posts': posts, 'thread': thread }
    return render(request, 'thread.html', context)
