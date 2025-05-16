from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from review.views import ReviewAPIView


app_name = 'review'
router = DefaultRouter()

router.register(r'reviews', ReviewAPIView, basename='review')


urlpatterns = [
    path('', include(router.urls)),
]
