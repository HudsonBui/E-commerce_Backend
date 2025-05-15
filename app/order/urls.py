from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from .views import (
    AddressViewSet,
    CouponViewSet,
    OrderViewSet,
)

router = DefaultRouter()
app_name = 'order'

router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
