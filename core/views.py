# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import SuspiciousOperation
from django.db import transaction
from django.db.models.aggregates import Max
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, reverse

from core.apps import CoreConfig
from core.models import Thread, Post, Section


def render_error(request, error):
    return render(request, 'error-page.html', { 'error': error }, status=400)


def get_active_thread_list(thread_from, thread_to, sectionid=None):
    threads = Post.objects
    
    if sectionid:
        threads = threads.filter(thread__section_id=sectionid)
    
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
        'datetime': thread['last_date']
    } for thread in threads ], more


def index(request):
    sections = []
    for section in Section.objects.all():
        threads, more = get_active_thread_list(0, 5, section.id)
        sections.append({
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'threads': threads
        })
    
    threads, more = get_active_thread_list(0, 5)
    context = {
        'activethreads': threads,
        'sections': sections
    }
    
    return render(request, 'index.html', context)


def post(request):
    current_user = request.user
    if not current_user.is_authenticated:
        return redirect('/accounts/login/?next=' + reverse('post'))
    
    try:
        tid = int(request.POST.get('tid'))
    except:
        return render_error(request, 'No thread id supplied')
    
    content = request.POST.get('content')
    if not content:
        return render_error(request, 'No content supplied')
    
    thread = Thread.objects.get(id=tid)
    post = Post(thread=thread, content=content, author=current_user)
    post.save()
    
    next = request.GET.get('next', '/threads/%d' % thread.id)
    return redirect(next)


def newthread(request):

    def default_post_page():
        sectionid = request.GET.get('sid')
        if sectionid is None:
            return render_error(request, 'No section id supplied')
        
        return render(request, 'newthread.html', {
            'sectionid': sectionid
        })
    
    current_user = request.user
    if not current_user.is_authenticated:
        return redirect('/accounts/login/?next=' + reverse('post'))
    
    try:
        sid = int(request.POST.get('sid'))
    except:
        return default_post_page()
    
    title = request.POST.get('title')
    content = request.POST.get('content')
    if content == '' or title == '':
        return render_error(request, 'No title or content supplied')
    
    if not content or not title:
        return default_post_page()
    
    try:
        section = Section.objects.get(id=sid)
    except:
        # no section
        return default_post_page()
    
    # create a thread if needed
    thread = Thread(title=title, creator=current_user, section=section)
    thread.save()
    
    post = Post(thread=thread, content=content, author=current_user)
    post.save()
    
    next = request.GET.get('next', '/threads/%d' % thread.id)
    
    return redirect(next)


def threads(request):
    try:
        section = Section.objects.get(id=request.GET.get('sid'))
    except:
        section = None
    
    page = int(request.GET.get('page', '0'))
    if page < 0:
        raise Http404
    
    thread_from = page * CoreConfig.threads_per_page
    thread_to = thread_from + CoreConfig.threads_per_page
    
    threads, more = get_active_thread_list(
        thread_from,
        thread_to,
        section.id if section else None
    )
    
    prev = None
    next = None
    
    if page > 0:
        prev = page - 1
    
    if more:
        next = page + 1
    
    context = {
        'threads': threads,
        'section': section,
        'prev': prev,
        'next': next
    }
    
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


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login')
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', { 'form': form })

