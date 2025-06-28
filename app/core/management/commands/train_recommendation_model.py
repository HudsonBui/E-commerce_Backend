from django.core.management.base import BaseCommand
from app.recommendation.ml_models.ncf_rs import (
    load_and_preprocess_data,
    train_model,
    get_recommendations
)


class Command(BaseCommand):
    help = 'Train the recommendation model'

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.SUCCESS(
                'Starting model training...'))

        # Preprocess data
        try:
            (interactions,
             user_encoder,
             product_encoder,
             num_users,
             num_products) = load_and_preprocess_data()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Error preprocessing data: {e}"))
            return

        # Train model
        try:
            model = train_model(
                interactions, num_users, num_products)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error training model: {e}"))
            return

        # Example: Get recommendations for a user
        if len(interactions) > 0:
            sample_user = interactions['user_id'].iloc[0]
            recommendations = get_recommendations(
                sample_user, model, user_encoder, product_encoder)
            self.stdout.write(
                self.style.SUCCESS(
                    "Sample recommendations for user "
                    f"{sample_user}: {recommendations}"))

        self.stdout.write(
            self.style.SUCCESS('Model training completed successfully!'))
