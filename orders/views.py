from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import Order
from .serializers import OrderSerializer, PlaceOrderSerializer
from .tasks import send_order_confirmation


class IsOrderOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """List + detail for the current user's orders."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrderOwner]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items', 'items__product')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.status != 'pending':
            return Response(
                {'detail': 'Only pending orders can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # restore stock inside a transaction so nothing gets lost
        with transaction.atomic():
            for item in order.items.select_related('product').all():
                if item.product:
                    item.product.stock_quantity += item.quantity
                    item.product.save(update_fields=['stock_quantity'])

            order.status = 'cancelled'
            order.save(update_fields=['status'])

        return Response(OrderSerializer(order).data)


class PlaceOrderView(generics.CreateAPIView):
    serializer_class = PlaceOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # send confirmation in the background
        # if celery/redis isnt running we still want the order to go through
        try:
            send_order_confirmation.delay(order.id)
        except Exception:
            pass

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
