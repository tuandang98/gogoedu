from django.apps import AppConfig
from django.db.models.signals import post_migrate


class GogoeduConfig(AppConfig):
    name = 'gogoedu'
    verbose_name = 'Gogo Edu'
