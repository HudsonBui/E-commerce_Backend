from rest_framework import serializers

from core.models import (
    Review,
    ReviewImage,
)


class ReviewImageSerializer(serializers.ModelSerializer):
    """Serializer for ReviewImage model"""
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ReviewImage
        fields = ['id', 'review', 'image']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    images = ReviewImageSerializer(many=True, required=False)

    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'product',
            'rating',
            'title',
            'content',
            'images',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """Create a new review"""
        images_data = validated_data.pop('images', [])
        review = Review.objects.create(**validated_data)

        for image_data in images_data:
            ReviewImage.objects.create(review=review, image=image_data)

        return review
