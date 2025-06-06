import os
import pickle
import numpy as np
from django.conf import settings
from tensorflow.keras.models import load_model
from core.models import Product, UserAction
from django.db.models import Sum
import logging


logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self):
        self.model = None
        self.user_encoder = None
        self.product_encoder = None
        self._load_models()

    def _load_models(self):
        """Load the trained model and encoders"""
        models_dir = os.path.join(
            settings.MEDIA_ROOT, 'ml_models')

        try:
            # Load model
            model_path = os.path.join(
                models_dir, 'ncf_model.h5')
            if os.path.exists(model_path):
                self.model = load_model(model_path)

            # Load encoders
            user_encoder_path = os.path.join(
                models_dir, 'user_encoder.pkl')
            product_encoder_path = os.path.join(
                models_dir, 'product_encoder.pkl')

            if os.path.exists(user_encoder_path):
                with open(user_encoder_path, 'rb') as f:
                    self.user_encoder = pickle.load(f)

            if os.path.exists(product_encoder_path):
                with open(product_encoder_path, 'rb') as f:
                    self.product_encoder = pickle.load(f)

        except Exception as e:
            logger.error(
                f"Error loading recommendation models: {e}")

    def get_user_recomm(self, user_id, top_n=5):
        """Get product recommendations for a user"""
        if not all([
                self.model, self.user_encoder, self.product_encoder]):
            logger.warning("Recommendation models not loaded")
            return Product.objects.none()

        try:
            if str(user_id) not in self.user_encoder.classes_:
                # Return popular products based on purchase actions
                popular_product_ids = UserAction.objects.filter(
                    event_type='purchase') \
                    .values('product_id') \
                    .annotate(total_score=Sum('score')) \
                    .order_by('-total_score')[:top_n] \
                    .values_list('product_id', flat=True)

                return Product.objects.filter(
                    id__in=popular_product_ids)

            user_idx = self.user_encoder.transform([str(user_id)])[0]
            product_indices = np.arange(
                len(self.product_encoder.classes_))
            user_array = np.array([user_idx] * len(product_indices))

            # Predict scores
            predictions = self.model.predict(
                [user_array, product_indices], batch_size=64)
            predictions = predictions.flatten()

            # Get top N products
            top_indices = np.argsort(predictions)[-top_n:][::-1]
            recommended_product_ids = self.product_encoder.inverse_transform(
                top_indices)

            # Return Django Product objects
            return Product.objects.filter(
                id__in=recommended_product_ids)

        except Exception as e:
            logger.error(
                f"Error generating recommendations for user {user_id}: {e}")
            return Product.objects.none()


# Global instance
recomm_svc = RecommendationService()
