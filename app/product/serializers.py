"""
Serializers for Product API.
"""
from rest_framework import serializers
from typing import List

from core.models import (
    ProductVariant,
    ProductDetailInformation,
    ProductDetail,
    Product,
    ProductImage,
    Category,
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category."""
    parent_category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'parent_category',
            'description',
        ]
        read_only_fields = ('id',)


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variant."""
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'product',
            'color',
            'size',
            'stock_quantity',
        ]
        read_only_fields = ('id',)


class ProductDetailInformationSerializer(serializers.ModelSerializer):
    """Serializer for product detail information."""
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProductDetailInformation
        fields = [
            'id',
            'product',
            'detail_name',
            'detail_value',
        ]
        read_only_fields = ('id',)


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product image."""
    url = serializers.URLField(required=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProductImage
        fields = [
            'id',
            'url',
            'product',
            'is_primary',
        ]
        read_only_fields = ('id',)


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail."""
    detail_variant = ProductVariantSerializer(required=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProductDetail
        fields = [
            'id',
            'product',
            'price',
            'detail_variant',
            'sale_price',
        ]

        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        """Update product detail."""
        detail_variant = validated_data.pop('detail_variant', None)
        if detail_variant is not None:
            instance.detail_variant, _ = ProductVariant.objects.get_or_create(
                **detail_variant
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ProductGenericSerializer(serializers.ModelSerializer):

    """Serializer for general product information."""
    original_price = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'images',
            'average_rating',
            'review_count',
            'price',
            'original_price',
            'sale_price'
        ]

    def get_original_price(self, obj):
        """Get original price of the product."""
        if not obj.product_details.exists():
            return 0.0

        return obj.product_details.order_by('price').first().price

    def get_sale_price(self, obj):
        """Get sale price of the product."""
        if not obj.product_details.exists():
            return 0.0

        return obj.product_details.order_by('price').first().sale_price



class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product."""
    product_details = ProductDetailSerializer(many=True)
    detail_information = ProductDetailInformationSerializer(
        many=True
    )
    images = ProductImageSerializer(many=True)
    categories = CategorySerializer(many=True, read_only=True)

    colors = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ProductGenericSerializer.Meta.fields + [
            'description',
            'material',
            'weight',
            'weight_unit',
            'stock_quantity',
            'node_name',
            'style',
            'currency',
            'detail_information',
            'categories',
            'colors',
            'sizes',
        ]

        read_only_fields = ('id',)

    def get_colors(self, obj) -> List[str]:
        variants = obj.variants.all()
        colors = [variant.color for variant in variants if variant.color]

        return sorted(set(colors))

    def get_sizes(self, obj) -> List[str]:
        variants = obj.variants.all()
        sizes = [variant.size for variant in variants if variant.size]

        return sorted(set(sizes))
