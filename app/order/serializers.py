from rest_framework import serializers
from core.models import (
    Order,
    OrderItem,
    Address,
    Coupon,
)
from product.serializers import ProductDetailSerializer


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model"""
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Address
        fields = [
            'id',
            'user',
            'recipient_name',
            'recipient_phone_number',
            'address_line',
            'country',
            'city',
            'state',
            'postal_code',
            'is_default',
        ]
        read_only_fields = ['id']


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model"""
    class Meta:
        model = Coupon
        fields = [
            'id',
            'code',
            'discount_percentage',
            'min_order_amount',
            'max_discount_amount',
            'usage_limit',
            'used_count',
            'start_date',
            'end_date',
            'is_active',
        ]
        read_only_fields = ['id']


class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    product_detail = ProductDetailSerializer()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order',
            'product_detail',
            'quantity',
            'total_price',
        ]
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    address = AddressSerializer(required=True)
    coupon = CouponSerializer(required=False, allow_null=True)
    items = OrderItemSerializer(many=True, required=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'address',
            'coupon',
            'items',
            'order_date',
            'total_amount',
            'discount_amount',
            'order_status',
        ]
        read_only_fields = ['id']

    def _get_product_variant_price(self, product_detail):
        """Get the price of the product variant"""
        original_price = product_detail.price
        sale_price = product_detail.sale_price
        if not sale_price:
            if not original_price:
                return 0
            else:
                return original_price
        else:
            if not original_price:
                return sale_price
            else:
                return min(sale_price, original_price)

    def create(self, validated_data):
        """Create a new order"""
        address_data = validated_data.pop('address')
        coupon_data = validated_data.pop('coupon', None)
        items_data = validated_data.pop('items')

        address_serializer = AddressSerializer(data=address_data)
        address_serializer.is_valid(raise_exception=True)
        address = address_serializer.save(user=self.context['request'].user)

        if coupon_data:
            coupon_serializer = CouponSerializer(data=coupon_data)
            coupon_serializer.is_valid(raise_exception=True)
            coupon = coupon_serializer.save()

        order = Order.objects.create(
            user=self.context['request'].user,
            address=address,
            coupon=coupon if coupon_data else None,
            **validated_data
        )

        for item in items_data:
            product_detail = item.get('product_detail')
            quantity = item.get('quantity')

            OrderItem.objects.create(
                order=order,
                product_detail=product_detail,
                quantity=quantity,
                total_price=self._get_product_variant_price(
                    product_detail
                    ) * quantity
            )

        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status"""
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    address = AddressSerializer(required=False)
    coupon = CouponSerializer(required=False, allow_null=True)
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'address',
            'coupon',
            'items',
            'order_date',
            'total_amount',
            'discount_amount',
            'order_status',
        ]
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        """Update the order status"""
        order_status = validated_data.get(
            'order_status',
            instance.order_status
        )
        instance.order_status = order_status
        instance.save()
        return instance
