from rest_framework import viewsets

from watched_list.serializers import UserWatchedProductSerializer
from core.models import UserWatchedProduct


class UserWatchedProductViewSet(viewsets.ModelViewSet):
    """Retrieve all and a single product"""
    queryset = UserWatchedProduct.objects.all()
    serializer_class = UserWatchedProductSerializer

    def get_queryset(self):
        """Retrieve products."""
        queryset = self.queryset
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(
                user=user
            ).distinct()
        else:
            queryset = queryset.none()
        return queryset

    def perform_create(self, serializer):
        """Create a new user watched product."""
        user = self.request.user
        serializer.save(user=user)
