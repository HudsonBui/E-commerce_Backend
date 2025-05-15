from rest_framework import viewsets

from order.serializers import (
    AddressSerializer,
    CouponSerializer,
    OrderSerializer,
    OrderUpdateSerializer
)

from core.models import (
    Address,
    Order,
    Coupon,
)


class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet for Address model"""
    serializer_class = AddressSerializer
    queryset = Address.objects.all()

    def get_queryset(self):
        """Return the list of addresses for the authenticated user"""
        user = self.request.user
        return Address.objects.filter(user=user).order_by('-is_default', '-id')

    def perform_create(self, serializer):
        """Create a new address for the authenticated user"""
        serializer.save(user=self.request.user)


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Coupon model."""
    serializer_class = CouponSerializer
    queryset = Coupon.objects.all()

    def get_queryset(self):
        """Return the list of coupons"""
        return Coupon.objects.filter(is_active=True).order_by('-id')


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order model"""
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        """Return the list of orders for the authenticated user"""
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-id')

    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action"""
        if self.action == 'update' or self.action == 'partial_update':
            return OrderUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new order for the authenticated user"""
        serializer.save(user=self.request.user)
