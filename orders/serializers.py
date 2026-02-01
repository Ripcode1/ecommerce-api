from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name',
            'product_price', 'quantity', 'subtotal',
        ]
        read_only_fields = ['product_name', 'product_price']


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user_email', 'status',
            'total_amount', 'shipping_address', 'notes',
            'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'order_number', 'total_amount',
            'created_at', 'updated_at',
        ]


class PlaceOrderSerializer(serializers.Serializer):
    """
    Validates stock, creates order + items, decrements inventory.
    """
    shipping_address = serializers.CharField()
    notes = serializers.CharField(required=False, default='')
    items = OrderItemCreateSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "Order must have at least one item."
            )

        for item in value:
            try:
                product = Product.objects.get(id=item['product_id'])
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f"Product {item['product_id']} not found."
                )

            if not product.is_active:
                raise serializers.ValidationError(
                    f"'{product.name}' is currently unavailable."
                )

            if product.stock_quantity < item['quantity']:
                raise serializers.ValidationError(
                    f"Not enough stock for '{product.name}'. "
                    f"Available: {product.stock_quantity}, "
                    f"requested: {item['quantity']}"
                )

        return value

    def create(self, validated_data):
        user = self.context['request'].user
        items_data = validated_data.pop('items')

        # lock rows so two orders cant oversell the same product
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                shipping_address=validated_data['shipping_address'],
                notes=validated_data.get('notes', ''),
            )

            for item_data in items_data:
                product = Product.objects.select_for_update().get(
                    id=item_data['product_id']
                )

                # double check stock now that we have the lock
                if product.stock_quantity < item_data['quantity']:
                    raise serializers.ValidationError(
                        f"Not enough stock for '{product.name}'. "
                        f"Available: {product.stock_quantity}"
                    )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_price=product.price,
                    quantity=item_data['quantity'],
                )

                product.stock_quantity -= item_data['quantity']
                product.save(update_fields=['stock_quantity'])

            order.calculate_total()
        return order
