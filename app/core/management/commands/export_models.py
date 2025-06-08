import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Export trained recommendation model to a specific directory'

    def add_arguments(self, parser):
        parser.add_argument(
            'target_dir',
            type=str,
            help='Target directory to export the model to')

    def handle(self, *args, **options):
        target_dir = options['target_dir']

        # Ensure target directory exists
        os.makedirs(target_dir, exist_ok=True)

        # Source directory
        source_dir = os.path.join(settings.MEDIA_ROOT, 'ml_models')

        # Check if source directory exists
        if not os.path.exists(source_dir):
            self.stdout.write(
                self.style.ERROR(
                    f'Source directory {source_dir} does not exist. '
                    'Please train a model first.')
            )
            return

        # List of files to export
        model_files = [
            'ncf_model.h5',
            'user_encoder.pkl',
            'product_encoder.pkl']

        # Copy each file
        for file_name in model_files:
            source_file = os.path.join(source_dir, file_name)
            if os.path.exists(source_file):
                target_file = os.path.join(target_dir, file_name)
                shutil.copy2(source_file, target_file)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Exported {file_name} to {target_file}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'File {file_name} not found in {source_dir}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Model export completed to {target_dir}')
        )
