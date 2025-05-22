from rest_framework import serializers

from core.models import (
    Product,
    UserWatchedProduct,
)

from product.serializers import ProductGenericSerializer


class UserWatchedProductSerializer(serializers.ModelSerializer):
    """Serializer for user watched product."""
    # Check if the generic product serializer works fine here
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )
    shown_product = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserWatchedProduct
        fields = [
            'id',
            'product',
            'shown_product',
            'created_at',
        ]
        read_only_fields = ('id',)

    def get_shown_product(self, obj) -> ProductGenericSerializer:
        """Get the product serializer."""
        product = obj.product
        serializer = ProductGenericSerializer(product)
        return serializer.data
