import os
import pickle
import numpy as np
from django.conf import settings
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import mse as mean_squared_error
from core.models import Product, UserAction
from django.db.models import Sum
import logging


logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self, model_dir=None):
        self.model = None
        self.user_encoder = None
        self.product_encoder = None
        self.model_dir = model_dir
        self._load_models()

    def _load_models(self):
        """Load the trained model and encoders"""
        # Use custom directory if provided, otherwise use default
        if self.model_dir:
            models_dir = self.model_dir
        else:
            models_dir = os.path.join(settings.MEDIA_ROOT, 'ml_models')

        try:
            # Load model
            model_path = os.path.join(models_dir, 'ncf_model.h5')
            print("Model path:", model_path)
            if os.path.exists(model_path):
                self.model = load_model(
                    model_path,
                    custom_objects={'mse': mean_squared_error})
                logger.info(f"Loaded model from {model_path}")
            else:
                logger.warning(f"Model file not found at {model_path}")

            # Load encoders
            user_encoder_path = os.path.join(models_dir, 'user_encoder.pkl')
            product_encoder_path = os.path.join(
                models_dir, 'product_encoder.pkl')

            if os.path.exists(user_encoder_path):
                with open(user_encoder_path, 'rb') as f:
                    self.user_encoder = pickle.load(f)
                logger.info(f"Loaded user encoder from {user_encoder_path}")
            else:
                logger.warning(
                    f"User encoder not found at {user_encoder_path}")

            if os.path.exists(product_encoder_path):
                with open(product_encoder_path, 'rb') as f:
                    self.product_encoder = pickle.load(f)
                logger.info(
                    f"Loaded product encoder from {product_encoder_path}")
            else:
                logger.warning(
                    f"Product encoder not found at {product_encoder_path}")

        except Exception as e:
            logger.error(f"Error loading recommendation models: {e}")

    def get_user_recomm(self, user_id, top_n=5):
        """Get product recommendations for a user"""
        if not all([
                self.model, self.user_encoder, self.product_encoder]):
            logger.warning("Recommendation models not loaded")
            return Product.objects.none()

        print('Found model and encoders, generating recommendations...')

        try:
            if str(user_id) not in self.user_encoder.classes_:
                # Return popular products based on purchase actions
                print("Returning popular products for new user...")
                popular_product_ids = UserAction.objects.filter(
                    event_type='purchase') \
                    .values('product_id') \
                    .annotate(total_score=Sum('score')) \
                    .order_by('-total_score')[:top_n] \
                    .values_list('product_id', flat=True)

                return Product.objects.filter(
                    id__in=[int(pid) for pid in popular_product_ids])

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
recomm_svc = RecommendationService(
    model_dir=getattr(settings, 'RECOMMENDATION_MODEL_DIR', None)
)
