from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('threads/', views.threads, name='threads'),
    re_path('^threads/(\\d+)', views.thread, name='thread'),
    path('post/', views.post, name='post'),
    path('newthread/', views.newthread, name='newthread'),
    path('accounts/signup/', views.signup, name='signup'),
]
