from django.core.management.base import BaseCommand
from core.models import UserAction


class Command(BaseCommand):
    help = 'Delete all UserAction records'

    def handle(self, *args, **options):
        user_actions = UserAction.objects.all()
        count = user_actions.count()

        self.stdout.write(self.style.SUCCESS(
                f'Found {count} user actions:'))

        for action in user_actions:
            self.stdout.write(
                f"ID: {action.id}, "
                f"User: {action.user}, "
                f"Action: {action.action_type}, "
                f"Date: {action.created_at}, ")
