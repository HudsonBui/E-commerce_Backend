from django.core.management.base import BaseCommand
from core.models import UserAction
from django.contrib.auth import get_user_model
from django.db import connection


class Command(BaseCommand):
    help = 'Delete all UserAction records'

    def handle(self, *args, **options):
        count, details = get_user_model().objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            f'Successfully deleted {count} users'
            ))

        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE core_user_id_seq RESTART WITH 1")

        self.stdout.write(self.style.SUCCESS('Successfully reset user ID sequence to 1'))
