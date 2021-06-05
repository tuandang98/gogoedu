from django.core.management import BaseCommand
from django_gamification.models import BadgeDefinition, Category, UnlockableDefinition, GamificationInterface

from gogoedu.models import myUser


class Command(BaseCommand):
    help = 'Generates fake data for the app'

    def handle(self, *args, **options):
        category_learned=Category.objects.create(name='Learned', description='These are the learned badges')

        kanji300=BadgeDefinition.objects.create(
            name='300 Kanjis learned',
            description='Learned 300 kanji',
            points=150,
            progression_target=300,
            category=category_learned,
        )
        word300=BadgeDefinition.objects.create(
            name='300 Words learned',
            description='Learned 300 words',
            points=150,
            progression_target=300,
            category=category_learned,
        )
        BadgeDefinition.objects.create(
            name='Alphabet Finished',
            description='Finished learning the alphabet',
            points=50,
            progression_target=100,
            
            category=category_learned,
        )
        BadgeDefinition.objects.create(
            name='100 Words learned',
            description='Learned 100 words',
            points=50,
            progression_target=100,
            next_badge=word300,
            category=category_learned,
        )
        BadgeDefinition.objects.create(
            name='100 Kanjis learned',
            description='Learned 100 kanji',
            points=50,
            progression_target=100,
            next_badge=kanji300,
            category=category_learned,
        )

        UnlockableDefinition.objects.create(
            name='Mission 20 quests',
            description='Take the mission get 20 quests per day',
            points_required=2000
        )
