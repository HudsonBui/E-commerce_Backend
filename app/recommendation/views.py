from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from recommendation.services import recomm_svc
from rest_framework import status
from core.models import UserAction, Product
import pandas as pd
from product.serializers import ProductGenericSerializer


class LogUserActionView(APIView):
    def post(self, request):
        user_id = request.user.id
        product_id = request.data.get('product_id')
        event_type = request.data.get('event_type')

        if not all([user_id, product_id, event_type]):
            return Response(
                {"error": "Missing required fields"},
                status=status.HTTP_400_BAD_REQUEST)

        # Validate product_id
        product_ids = Product.objects.all().values_list(
            'id', flat=True)
        if product_id not in product_ids.astype(str):
            return Response(
                {"error": "Invalid product_id"},
                status=status.HTTP_400_BAD_REQUEST)

        event_weights = {
            'view': 1.0,
            'cart': 3.0,
            'purchase': 5.0,
            'remove_from_cart': -1.0}
        score = event_weights.get(event_type, 1.0)

        UserAction.objects.create(
            user_id=user_id,
            product_id=product_id,
            event_type=event_type,
            event_time=pd.Timestamp.now(),
            score=score
        )
        return Response(
            {"status": "Action logged"},
            status=status.HTTP_201_CREATED)


class RecommendationViewSet(viewsets.ViewSet):
    """ViewSet for user recommendations"""

    @action(detail=False, methods=['get'])
    def for_user(self, request):
        """Get recommendations for the authenticated user"""
        user = request.user
        top_n = int(request.query_params.get('limit', 5))

        recommended_products = recomm_svc.get_user_recomm(
            user_id=user.id,
            top_n=top_n
        )

        serializer = ProductGenericSerializer(
            recommended_products, many=True)
        return Response({
            'recommendations': serializer.data,
            'count': len(serializer.data)
        })
