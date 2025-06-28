"""
Serializer for the Cart API.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from core.models import (
    Cart,
    CartItem,
    ProductDetail,
    ProductVariant,
)

from product.serializers import (
    ProductDetailSerializer,
    ProductGenericSerializer,
)

import logging


logger = logging.getLogger(__name__)


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""
    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
        ]


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart."""
    cart = CartSerializer(read_only=True)
    product_detail = ProductDetailSerializer()
    generic_product_info = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'cart',
            'generic_product_info',
            'product_detail',
            'update_date',
            'is_checked',
            'quantity',
        ]
        read_only_fields = ('id',)

    @extend_schema_field(ProductGenericSerializer)
    def get_generic_product_info(self, obj):
        """Get generic product information"""
        product = obj.product_detail.product if obj.product_detail else None
        if product is None:
            logger.warning("Product not found for the given product detail.")
            return {}
        serializer = ProductGenericSerializer(product, context=self.context)
        return serializer.data

    def create(self, validated_data):
        """Create a new cart item if it does not exist"""
        product_detail_data = validated_data.pop('product_detail', None)
        cart = Cart.objects.get(user=self.context['request'].user)

        if product_detail_data is None:
            logger.error("Product detail is required to create a cart item.")
            raise serializers.ValidationError("Product detail is required.")

        # Extract detail_variant data and handle it separately
        variant_data = product_detail_data.pop('detail_variant', None)
        print(f"detail_variant_data: {variant_data}, type: {type(variant_data)}")
        variant_id = variant_data.get('id') if variant_data else None

        # Create a clean query dict with just the fields that match the model
        query_params = {}

        if 'product' in product_detail_data:
            print(f"Check: {product_detail_data['product']}")
            query_params['product'] = product_detail_data['product']

        if 'price' in product_detail_data:
            print(f"Check: {product_detail_data['price']}")
            query_params['price'] = product_detail_data['price']

        if 'sale_price' in product_detail_data:
            print(f"Check: {product_detail_data['sale_price']}")
            query_params['sale_price'] = product_detail_data['sale_price']

        # Add the variant if we found an ID
        if variant_id:
            try:
                print(f"Check: {variant_id}")
                variant = ProductVariant.objects.get(id=variant_id)
                query_params['detail_variant'] = variant
            except ProductVariant.DoesNotExist:
                logger.error(f"Variant with ID {variant_id} not found")
                raise serializers.ValidationError(f"Variant with ID {variant_id} not found")

        try:
            product_detail = ProductDetail.objects.get(**query_params)
        except ProductDetail.DoesNotExist:
            logger.error("Product detail not found.")
            raise serializers.ValidationError("Product detail not found.")

        # Check if the cart item already exists
        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product_detail=product_detail
            )
            cart_item.quantity += validated_data.get('quantity', 1)
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            # Create a new cart item if it does not exist
            cart_item = CartItem.objects.create(
                cart=cart,
                product_detail=product_detail,
                **validated_data
            )
            return cart_item

    def update(self, instance, validated_data):
        """Update cart item"""
        # Verify cart item belongs to user
        cart = Cart.objects.get(user=self.context['request'].user)
        if instance.cart.id != cart.id:
            logger.error(
                "You do not have permission to update this cart item."
            )
            raise serializers.ValidationError(
                "You do not have permission to update this cart item."
            )

        # Handle product detail changes
        product_detail_data = validated_data.pop('product_detail', None)
        if product_detail_data is not None:
            # Extract detail_variant data and handle it separately
            variant_data = product_detail_data.pop('detail_variant', None)
            print(f"detail_variant_data: {variant_data}, type: {type(variant_data)}")
            variant_id = variant_data.get('id') if variant_data else None

            # Create a clean query dict with just the fields that match the model
            query_params = {}

            if 'product' in product_detail_data:
                query_params['product'] = product_detail_data['product']

            if 'price' in product_detail_data:
                query_params['price'] = product_detail_data['price']

            if 'sale_price' in product_detail_data:
                query_params['sale_price'] = product_detail_data['sale_price']

            # Add the variant if we found an ID
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id)
                    query_params['detail_variant'] = variant
                except ProductVariant.DoesNotExist:
                    logger.error(f"Variant with ID {variant_id} not found")
                    raise serializers.ValidationError(f"Variant with ID {variant_id} not found")

            try:
                product_detail = ProductDetail.objects.get(**query_params)
                instance.product_detail = product_detail
            except ProductDetail.DoesNotExist:
                logger.error("Product detail not found.")
                raise serializers.ValidationError("Product detail not found.")

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
