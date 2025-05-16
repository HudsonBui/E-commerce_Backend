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

from drf_spectacular.utils import extend_schema, OpenApiParameter


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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='order_status',
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """Return the list of orders for the authenticated user"""
        user = self.request.user
        order_status = self.request.query_params.get('order_status')
        if order_status:
            return Order.objects.filter(
                user=user,
                order_status=order_status
            ).order_by('-order_date')
        return Order.objects.filter(user=user).order_by('-order_date')

    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action"""
        if self.action == 'update' or self.action == 'partial_update':
            return OrderUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new order for the authenticated user"""
        serializer.save(user=self.request.user)
