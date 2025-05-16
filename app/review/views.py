from rest_framework import (
    viewsets,
    mixins,
)

from review.serializers import ReviewSerializer

from core.models import (
    Review,
    ProductDetail,
)


class ReviewAPIView(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    """ViewSet for Review model"""
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get_queryset(self):
        """Return the list of reviews for the authenticated user"""
        user = self.request.user
        return Review.objects.filter(user=user).order_by(
            '-created_at'
        ).prefetch_related('images')

    def perform_create(self, serializer):
        """Create a new review."""
        user = self.request.user
        product_id = self.request.data.get('product_id')

        try:
            product = ProductDetail.objects.get(id=product_id)
            serializer.save(user=user, product=product)
        except ProductDetail.DoesNotExist:
            raise serializer.ValidationError(
                {"product_id": "Invalid product ID"}
            )
