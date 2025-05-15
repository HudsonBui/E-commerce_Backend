from rest_framework import (
    viewsets,
)
from cart.serializers import CartItemSerializer
from core.models import CartItem, Cart


class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the Cart API.
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        cart = Cart.objects.filter(user=self.request.user).first()
        return CartItem.objects.filter(cart=cart).prefetch_related(
            'cart',
            'product_detail__detail_variant',
        )
