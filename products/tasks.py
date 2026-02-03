from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def notify_low_stock(product_id):
    """
    Check if a product is running low and log an alert.
    
    In production this would send an email or slack message to the seller,
    but for now it just logs it. Good enough for the demo.
    """
    from .models import Product

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        logger.warning(f"Product {product_id} not found - might have been deleted")
        return

    if product.stock_quantity < 5:
        logger.info(
            f"LOW STOCK: {product.name} (SKU: {product.sku}) "
            f"has {product.stock_quantity} units left"
        )
        # TODO: send actual email/slack notification
        # something like:
        # send_email(product.seller.email, subject="Low Stock Alert", ...)

    return f"Checked stock for product {product_id}"


@shared_task
def update_product_ratings():
    """
    Batch job to recompute average ratings.
    Would be scheduled with celery beat in production (eg. every hour).
    """
    from django.db.models import Avg
    from .models import Product

    products = Product.objects.annotate(avg=Avg('reviews__rating'))
    count = 0
    for p in products:
        if p.avg is not None:
            logger.info(f"{p.name}: avg rating = {p.avg:.1f}")
            count += 1

    return f"Updated ratings for {count} products"
