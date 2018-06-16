from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('threads/', views.threads, name='active_threads'),
 re_path('^threads/(?P<sid>\\d+)/', views.threads, name='section_threads'),
 re_path('^thread/(?P<tid>\\d+)/', views.thread, name='thread'),
    path('post/', views.post, name='post'),
 re_path('^newthread/(?P<sid>\\d+)/', views.newthread, name='newthread'),
    path('accounts/signup/', views.signup, name='signup'),
]
