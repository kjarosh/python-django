# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import SuspiciousOperation
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, reverse

from core.apps import CoreConfig
from core.models import Thread, Post, Section


def render_error(request, error):
    return render(request, 'error-page.html', { 'error': error }, status=400)


def get_page_number(request):
    try:
        page = int(request.GET.get('page', '0'))
    except:
        raise Http404
    if page < 0:
        raise Http404
    return page


def index(request):
    sections = []
    for section in Section.objects.all():
        threads, more = Thread.objects.active_threads(0, 5, section.id)
        sections.append({
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'threads': threads
        })
    
    threads, more = Thread.objects.active_threads(0, 5)
    context = {
        'activethreads': threads,
        'sections': sections
    }
    
    return render(request, 'index.html', context)


@login_required
def post(request):
    current_user = request.user
    
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
    
    next = request.GET.get('next', reverse('thread', thread.id))
    return redirect(next)


@login_required
def newthread(request, sid):

    def default_post_page(error=None):
        return render(request, 'newthread.html', {
            'error': error,
            'section': Section.objects.get(id=sid)
        })
    
    current_user = request.user
    
    title = request.POST.get('title')
    content = request.POST.get('content')
    if content == '' or title == '':
        return default_post_page('No title or content supplied')
    
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
    
    next = request.GET.get('next', reverse('thread', args=[thread.id]))
    
    return redirect(next)


def threads(request, sid=None):
    try:
        section = Section.objects.get(id=sid)
    except:
        section = None
    
    page = get_page_number(request)
    
    thread_from = page * CoreConfig.threads_per_page
    thread_to = thread_from + CoreConfig.threads_per_page
    
    threads, more = Thread.objects.active_threads(
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
        'sections': Section.objects.all(),
        'prev': prev,
        'next': next
    }
    
    return render(request, 'threads.html', context)


def thread(request, tid):
    page = get_page_number(request)
    
    try:
        thread = Thread.objects.get(id=tid)
    except ObjectDoesNotExist:
        raise Http404
    
    post_from = page * CoreConfig.posts_per_page
    post_to = post_from + CoreConfig.posts_per_page
    posts = Post.objects \
        .filter(thread=tid) \
        .order_by('time_posted')[post_from:post_to + 1]
    
    if len(posts) == 0:
        raise Http404
    
    more = (len(posts) == post_to - post_from + 1)
    posts = posts[0:post_to - post_from]
    
    prev = None
    next = None
    
    if page > 0:
        prev = page - 1
    
    if more:
        next = page + 1
    
    context = {
        'posts': posts,
        'thread': thread,
        'prev': prev,
        'next': next
    }
    return render(request, 'thread.html', context)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('login'))
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', { 'form': form })
