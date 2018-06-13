from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    
    posts_per_page = 15
    threads_per_page = 30
