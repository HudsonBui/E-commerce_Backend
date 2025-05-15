"""
URLs mapping for the product app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from product.views import (
    ProductListView,
    CategoryViewSet,
)

router = DefaultRouter()
router.register(
    r'products/generic',
    ProductListView,
    basename='product-generic'
)
router.register(r'categories', CategoryViewSet, basename='category')

app_name = 'product'

urlpatterns = [
    path('', include(router.urls)),
]
