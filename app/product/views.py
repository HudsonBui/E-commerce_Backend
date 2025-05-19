from rest_framework import (
    viewsets,
    pagination,
)
from product.serializers import (
    ProductSerializer,
    ProductGenericSerializer,
    CategorySerializer,
)
from core.models import (
    Product,
    Category,
)
from drf_spectacular.utils import extend_schema, OpenApiParameter


class ProductListView(viewsets.ReadOnlyModelViewSet):
    """List products API View."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = pagination.PageNumberPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='category_id',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Filter by category ID'
            ),
            OpenApiParameter(
                name='name',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by product name (case-insensitive)'
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """Retrieve products."""
        queryset = self.queryset
        category_id = self.request.query_params.get('category_id')
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        if self.action == 'list':
            # Optimize for ProductGenericSerializer
            queryset = queryset.prefetch_related(
                'product_details__detail_variant'
            )
        else:
            # Optimize for ProductSerializer (retrieve)
            queryset = queryset.prefetch_related(
                'product_details__detail_variant',
                'category',
                'images',
                'detail_information',
                'variants'
            )
        return queryset.distinct()

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return ProductGenericSerializer
        return self.serializer_class


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Retrieve all and a single product"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
