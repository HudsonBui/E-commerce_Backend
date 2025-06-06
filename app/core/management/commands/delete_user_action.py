from django.core.management.base import BaseCommand
from core.models import UserAction


class Command(BaseCommand):
    help = 'Delete all UserAction records'

    def handle(self, *args, **options):
        count, details = UserAction.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            f'Successfully deleted {count} user actions'
            ))
