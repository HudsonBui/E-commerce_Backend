from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from watched_list.views import UserWatchedProductViewSet


router = DefaultRouter()
router.register(
    r'product-history',
    UserWatchedProductViewSet,
    basename='user-watched-product'
)

app_name = 'watched_list'

urlpatterns = [
    path('', include(router.urls)),
]
