from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Category, Product
from .models import Order

User = get_user_model()


class OrderTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.seller = User.objects.create_user(
            email='seller@test.com', username='seller',
            password='Pass123!', is_seller=True,
        )
        self.buyer = User.objects.create_user(
            email='buyer@test.com', username='buyer', password='Pass123!',
        )

        cat = Category.objects.create(name='Gadgets')
        self.product = Product.objects.create(
            name='Bluetooth Speaker', description='Portable speaker',
            price='49.99', sku='BS-001', stock_quantity=10,
            category=cat, seller=self.seller,
        )

    def _place_order(self):
        """Helper: place an order as the buyer."""
        self.client.force_authenticate(user=self.buyer)
        return self.client.post('/api/v1/orders/place/', {
            'shipping_address': '123 Test St, Cape Town',
            'items': [{'product_id': self.product.id, 'quantity': 2}],
        }, format='json')

    def test_place_order(self):
        resp = self._place_order()
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)

    def test_order_total(self):
        resp = self._place_order()
        # 49.99 * 2 = 99.98
        self.assertEqual(float(resp.data['total_amount']), 99.98)

    def test_not_enough_stock(self):
        self.client.force_authenticate(user=self.buyer)
        resp = self.client.post('/api/v1/orders/place/', {
            'shipping_address': '123 Test St',
            'items': [{'product_id': self.product.id, 'quantity': 999}],
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_cancel_restores_stock(self):
        self._place_order()
        order = Order.objects.first()

        resp = self.client.post(f'/api/v1/orders/{order.id}/cancel/')
        self.assertEqual(resp.status_code, 200)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 10)

    def test_other_user_cant_see_my_orders(self):
        self._place_order()

        other = User.objects.create_user(
            email='other@test.com', username='other', password='Pass123!',
        )
        self.client.force_authenticate(user=other)
        resp = self.client.get('/api/v1/orders/')
        self.assertEqual(len(resp.data['results']), 0)

    def test_must_be_logged_in(self):
        self.client.logout()
        resp = self.client.post('/api/v1/orders/place/', {
            'shipping_address': '123 Test St',
            'items': [{'product_id': self.product.id, 'quantity': 1}],
        }, format='json')
        self.assertEqual(resp.status_code, 401)
