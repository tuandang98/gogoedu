from django.core.management import BaseCommand
from django_gamification.models import BadgeDefinition, Category, UnlockableDefinition, GamificationInterface

from gogoedu.models import myUser


class Command(BaseCommand):
    help = 'Generates fake data for the app'

    def handle(self, *args, **options):
        category_tested=Category.objects.create(name='Tested Badges', description='These are the tested badges')

        Diamond=BadgeDefinition.objects.create(
            name='Diamond',
            description='Congratulation Diamond',
            points=100,
            progression_target=1500,
            category=category_tested,
        )
        
        Gold=BadgeDefinition.objects.create(
            name='Gold',
            description='Congratulation Gold',
            points=100,
            progression_target=700,
            next_badge=Diamond,
            category=category_tested,
        )

        Silver=BadgeDefinition.objects.create(
            name='Silver',
            description='Congratulation Silver',
            points=100,
            progression_target=300,
            next_badge=Gold,
            category=category_tested,
        )

        BadgeDefinition.objects.create(
            name='Bronze',
            description='Congratulation Bronze',
            points=50,
            progression_target=100,
            next_badge=Silver,
            category=category_tested,
        )

        UnlockableDefinition.objects.create(
            name='Some super sought after feature',
            description='You unlocked a super sought after feature',
            points_required=50
        )
