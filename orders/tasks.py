from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_order_confirmation(order_id):
    """
    Send order confirmation to the customer.
    Just logging for now - would hook up to SendGrid or something in prod.
    """
    from .models import Order

    try:
        order = Order.objects.select_related('user').get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return

    logger.info(
        f"ORDER CONFIRMED: #{order.order_number} | "
        f"{order.user.email} | "
        f"{order.items.count()} items | ${order.total_amount}"
    )
    # TODO: wire up actual email service
    return f"Confirmation sent for order {order.order_number}"


@shared_task
def cancel_stale_orders():
    """
    Auto-cancel orders stuck in pending for over 24 hours.
    Designed to run on a schedule via celery beat.
    """
    from django.utils import timezone
    from django.db import transaction
    from datetime import timedelta
    from .models import Order

    cutoff = timezone.now() - timedelta(hours=24)
    stale = Order.objects.filter(status='pending', created_at__lt=cutoff)

    count = 0
    for order in stale:
        with transaction.atomic():
            for item in order.items.select_related('product').all():
                if item.product:
                    item.product.stock_quantity += item.quantity
                    item.product.save(update_fields=['stock_quantity'])
            order.status = 'cancelled'
            order.save(update_fields=['status'])
            count += 1

    logger.info(f"Cancelled {count} stale orders")
    return f"Cancelled {count} stale orders"
