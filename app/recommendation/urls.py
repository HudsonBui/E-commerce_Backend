"""
URL mappings for the user API.
"""
from django.urls import path

from recommendation import views

app_name = 'recommendation'

urlpatterns = [
    path(
      'user-action/',
      views.LogUserActionView.as_view(),
      name='user-action'),
    path(
        'recommended-products/',
        views.RecommendationViewSet.as_view({'get': 'for_user'}),
        name='recommended-products',
    ),
]
