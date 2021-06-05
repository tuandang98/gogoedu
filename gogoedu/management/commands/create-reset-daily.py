from django.core.management import BaseCommand

from gogoedu.models import myUser,Mission
from gogoedu.views import reset_daily
import datetime
class Command(BaseCommand):
    help = 'Generates fake data for the app'

    def handle(self, *args, **options):
        reset_daily(schedule=5,repeat=60*60*24, repeat_until=None)
