import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from core.models import UserAction, Product


class Command(BaseCommand):
    help = 'Import user actions from user_event.csv'

    def add_arguments(self, parser):
        parser.add_argument('event_file', type=str)

    def handle(self, *args, **options):
        try:
            event_file = options['event_file']
            self.stdout.write(f"Attempting to read file: {event_file}")

            # Load data
            events = pd.read_csv(event_file)
            self.stdout.write(
                f"Successfully loaded CSV with {len(events)} rows")

            # Get product IDs from the database
            available_product_ids = list(
                Product.objects.values_list('id', flat=True))

            if not available_product_ids:
                self.stdout.write(self.style.ERROR(
                    'No products found in the database. '
                    'Please add products first.'
                ))
                return

            # Convert IDs to strings to match the format used in UserAction
            available_product_ids = [str(pid) for pid in available_product_ids]

            # Filter valid events
            valid_events = events[
                events['event_type'].isin(
                    ['view', 'cart', 'purchase', 'remove_from_cart']
                )
                ]

            self.stdout.write("Mapping valid events to product IDs")
            # Map product IDs to ASINs
            np.random.seed(42)
            valid_events['mapped_product_id'] = np.random.choice(
                available_product_ids, size=len(valid_events)
            )

            # Assign scores
            event_weights = {
                'view': 1.0,
                'cart': 3.0,
                'purchase': 5.0,
                'remove_from_cart': -1.0
            }
            valid_events['score'] = valid_events[
                'event_type'].map(event_weights)

            self.stdout.write(
                f"Start to create UserAction objects for "
                f"{len(valid_events)} valid events")
            # Import to UserAction
            batch_size = 1000
            total_created = 0

            for batch_start in range(0, len(valid_events), batch_size):
                batch_end = min(
                    batch_start + batch_size, len(valid_events))
                batch = valid_events.iloc[batch_start:batch_end]

                user_actions = [
                    UserAction(
                        user_id=str(row['user_id']),
                        product_id=row['mapped_product_id'],
                        event_type=row['event_type'],
                        event_time=pd.to_datetime(row['event_time']),
                        score=row['score']
                    )
                    for _, row in batch.iterrows()
                ]

                # Create batch and report progress
                try:
                    UserAction.objects.bulk_create(
                        user_actions, batch_size=len(user_actions))
                    total_created += len(user_actions)
                    self.stdout.write(
                        f"Progress: {total_created}/{len(valid_events)}"
                        " records created "
                        f"({(total_created/len(valid_events)*100):.1f}%)"
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Error in batch {batch_start}-{batch_end}: {e}"))
                    raise  # Re-raise to stop processing and debug

                # Free memory
                del user_actions
                del batch

            self.stdout.write(self.style.SUCCESS(
                'Imported user actions successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            return
