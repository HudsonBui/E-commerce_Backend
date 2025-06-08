import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input,
    Embedding,
    Dense,
    Concatenate,
    Flatten)
import pickle
import os
from django.conf import settings
from django.db.models import Sum

# Import models
from core.models import UserAction, Product


# Step 1: Load and Preprocess Data from Django models
def load_and_preprocess_data():
    """Load user actions from database
    and preprocess data for model training"""
    # Fetch user actions from database
    actions = UserAction.objects.filter(
        event_type__in=[
            'view', 'cart', 'purchase', 'remove_from_cart'])

    if actions.count() == 0:
        raise ValueError(
            "No user actions in database and no product file provided")

    # Convert queryset to DataFrame
    actions_df = pd.DataFrame.from_records(
        actions.values('user_id', 'product_id', 'event_type', 'score')
    )

    # Get valid product IDs from database
    product_ids = list(Product.objects.values_list('id', flat=True))
    if not product_ids:
        raise ValueError(
            "No products found in the database. "
            "Please add products first."
        )
    actions_df = actions_df[
        actions_df['product_id'].astype(str).isin(
            [str(id) for id in product_ids])]

    if len(actions_df) == 0:
        raise ValueError(
            "No valid user actions with existing products found")

    # Aggregate interactions by user and product
    interactions = actions_df.groupby(
        ['user_id', 'product_id'])['score'].sum().reset_index()

    # Encode user and product IDs
    user_encoder = LabelEncoder()
    product_encoder = LabelEncoder()
    interactions['user_idx'] = user_encoder.fit_transform(
        interactions['user_id'].astype(str))
    interactions['product_idx'] = product_encoder.fit_transform(
        interactions['product_id'].astype(str))

    # Save encoders for inference
    models_dir = getattr(
        settings, 'RECOMMENDATION_MODEL_DIR',
        os.path.join(settings.MEDIA_ROOT, 'trained_model'))
    os.makedirs(models_dir, exist_ok=True)

    with open(os.path.join(
            models_dir, 'user_encoder.pkl'), 'wb') as f:
        pickle.dump(user_encoder, f)
    with open(os.path.join(
            models_dir, 'product_encoder.pkl'), 'wb') as f:
        pickle.dump(product_encoder, f)

    print(f"Processed {len(interactions)} user-product interactions")
    return (
        interactions,
        user_encoder,
        product_encoder,
        len(user_encoder.classes_),
        len(product_encoder.classes_))


# Step 2: Build Neural Collaborative Filtering Model
def build_ncf_model(num_users, num_products, embedding_dim=50):
    """Build a neural collaborative filtering model"""
    # Input layers
    user_input = Input(shape=(1,), name='user_input')
    product_input = Input(shape=(1,), name='product_input')

    # Embedding layers
    user_embedding = Embedding(
        num_users,
        embedding_dim,
        name='user_embedding')(user_input)
    product_embedding = Embedding(
        num_products,
        embedding_dim,
        name='product_embedding')(product_input)

    # Flatten embeddings
    user_vec = Flatten()(user_embedding)
    product_vec = Flatten()(product_embedding)

    # Concatenate user and product embeddings
    concat = Concatenate()([user_vec, product_vec])

    # Dense layers
    dense = Dense(128, activation='relu')(concat)
    dense = Dense(64, activation='relu')(dense)
    output = Dense(1, activation='sigmoid')(dense)

    # Build and compile model
    model = Model(
        inputs=[user_input, product_input], outputs=output)
    model.compile(
        optimizer='adam', loss='mse', metrics=['mae'])

    return model


# Step 3: Train the Model
def train_model(interactions, num_users, num_products):
    """Train the recommendation
    model with user interactions"""
    print(
        f"Training model with {len(interactions)} interactions")

    # Normalize scores to [0, 1] for sigmoid output
    min_score = interactions['score'].min()
    max_score = interactions['score'].max()

    # Handle case where all scores are the same
    if max_score == min_score:
        print(
            "Warning: All scores are identical. "
            "Using a default normalization range.")
        interactions['score_normalized'] = \
            (interactions['score'] - min_score + 1) / \
            (max_score - min_score + 2)
    else:
        interactions['score_normalized'] = \
            (interactions['score'] - min_score) / \
            (max_score - min_score)

    # Split data
    user_indices = interactions['user_idx'].values
    product_indices = interactions['product_idx'].values
    y = interactions['score_normalized'].values

    # Split data for user indices,
    # product indices, and scores separately
    (user_train, user_test,
     product_train, product_test,
     y_train, y_test) = train_test_split(
        user_indices,
        product_indices,
        y,
        test_size=0.2,
        random_state=42
    )

    # Build model
    model = build_ncf_model(num_users, num_products)

    model.fit(
        [user_train, product_train], y_train,
        validation_data=([user_test, product_test], y_test),
        epochs=10,
        batch_size=64,
        verbose=1
    )

    # Save model
    models_dir = getattr(
        settings, 'RECOMMENDATION_MODEL_DIR',
        os.path.join(settings.MEDIA_ROOT, 'trained_model'))
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(
        models_dir, 'ncf_model.h5')
    model.save(model_path)

    print(f"Model saved to {model_path}")
    return model


# Step 4: Generate Recommendations
def get_recommendations(
        user_id,
        model,
        user_encoder,
        product_encoder,
        top_n=5):
    """Get product recommendations for a specific user"""

    # Check if user exists in the model
    if str(user_id) not in user_encoder.classes_:
        print(
            f"User {user_id} not in trained model,"
            " returning popular products")
        # Fallback: Recommend popular products for new users
        try:
            popular_products = UserAction.objects.filter(
                    event_type__in=[
                        'purchase',
                        'cart',
                        'view']) \
                .values('product_id') \
                .annotate(total_score=Sum('score')) \
                .order_by('-total_score')[:top_n] \
                .values_list('product_id', flat=True)
            return list(popular_products)
        except Exception as e:
            print(f"Error getting popular products: {e}")
            return []

    user_idx = user_encoder.transform([str(user_id)])[0]
    product_indices = np.arange(len(product_encoder.classes_))
    user_array = np.array([user_idx] * len(product_indices))

    # Predict scores
    batch_size = min(64, len(product_indices))
    predictions = model.predict(
        [user_array, product_indices],
        batch_size=batch_size)
    predictions = predictions.flatten()

    # Get top N products
    top_indices = np.argsort(predictions)[-top_n:][::-1]
    recommended_products = product_encoder.inverse_transform(
        top_indices)

    return recommended_products.tolist()
