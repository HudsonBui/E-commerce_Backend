from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from cart.views import CartItemViewSet


router = DefaultRouter()
router.register(r'cart-item', CartItemViewSet, basename='cart-item')

app_name = 'cart'

urlpatterns = [
    path('', include(router.urls)),
]
