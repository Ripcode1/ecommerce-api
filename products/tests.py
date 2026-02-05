from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from .models import Category, Product

User = get_user_model()


class CategoryTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email='admin@test.com', username='admin', password='AdminPass123!'
        )

    def test_list_categories(self):
        Category.objects.create(name='Electronics')
        Category.objects.create(name='Clothing')

        resp = self.client.get('/api/v1/categories/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 2)

    def test_create_category_requires_admin(self):
        resp = self.client.post(
            '/api/v1/categories/', {'name': 'Books'}, format='json'
        )
        self.assertEqual(resp.status_code, 401)

    def test_admin_can_create(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(
            '/api/v1/categories/', {'name': 'Books'}, format='json'
        )
        self.assertEqual(resp.status_code, 201)


class ProductTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(
            email='seller@test.com', username='seller',
            password='SellerPass123!', is_seller=True,
        )
        self.buyer = User.objects.create_user(
            email='buyer@test.com', username='buyer',
            password='BuyerPass123!', is_seller=False,
        )
        self.category = Category.objects.create(name='Electronics')

        self.product_data = {
            'name': 'Wireless Mouse',
            'description': 'A nice wireless mouse for everyday use',
            'price': '29.99',
            'sku': 'WM-001',
            'stock_quantity': 50,
            'category_id': self.category.id,
        }

    def _create_product(self):
        self.client.force_authenticate(user=self.seller)
        return self.client.post(
            '/api/v1/products/', self.product_data, format='json'
        )

    def test_seller_can_create(self):
        resp = self._create_product()
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)

    def test_buyer_cant_create(self):
        self.client.force_authenticate(user=self.buyer)
        resp = self.client.post(
            '/api/v1/products/', self.product_data, format='json'
        )
        self.assertEqual(resp.status_code, 403)

    def test_list_products(self):
        self._create_product()
        self.client.logout()

        resp = self.client.get('/api/v1/products/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)

    def test_filter_by_price_range(self):
        self._create_product()
        self.client.logout()

        # should find it - price is 29.99
        resp = self.client.get('/api/v1/products/?min_price=20&max_price=40')
        self.assertEqual(len(resp.data['results']), 1)

        # too expensive filter - shouldnt find anything
        resp = self.client.get('/api/v1/products/?min_price=50')
        self.assertEqual(len(resp.data['results']), 0)

    def test_filter_by_category(self):
        self._create_product()
        self.client.logout()

        resp = self.client.get('/api/v1/products/?category=electronics')
        self.assertEqual(len(resp.data['results']), 1)

    def test_search(self):
        self._create_product()
        self.client.logout()

        resp = self.client.get('/api/v1/products/?search=wireless')
        self.assertEqual(len(resp.data['results']), 1)

    def test_ordering_by_price(self):
        self._create_product()

        # add a cheaper product
        data2 = self.product_data.copy()
        data2.update({'name': 'USB Cable', 'sku': 'USB-001', 'price': '9.99'})
        self.client.force_authenticate(user=self.seller)
        self.client.post('/api/v1/products/', data2, format='json')

        self.client.logout()
        resp = self.client.get('/api/v1/products/?ordering=price')
        results = resp.data['results']
        self.assertLessEqual(float(results[0]['price']), float(results[1]['price']))


class ReviewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(
            email='seller2@test.com', username='seller2',
            password='Pass123!', is_seller=True,
        )
        self.buyer = User.objects.create_user(
            email='buyer2@test.com', username='buyer2', password='Pass123!',
        )
        cat = Category.objects.create(name='Books')
        self.product = Product.objects.create(
            name='Django for Beginners', description='A great book',
            price='39.99', sku='BK-001', stock_quantity=10,
            category=cat, seller=self.seller,
        )

    def test_add_review(self):
        self.client.force_authenticate(user=self.buyer)
        resp = self.client.post(
            f'/api/v1/products/{self.product.slug}/reviews/',
            {'rating': 4, 'comment': 'Really helpful'},
            format='json',
        )
        self.assertEqual(resp.status_code, 201)

    def test_no_duplicate_reviews(self):
        self.client.force_authenticate(user=self.buyer)

        # first review should work
        self.client.post(
            f'/api/v1/products/{self.product.slug}/reviews/',
            {'rating': 4, 'comment': 'Great'},
            format='json',
        )
        # second one should fail
        resp = self.client.post(
            f'/api/v1/products/{self.product.slug}/reviews/',
            {'rating': 5, 'comment': 'Changed my mind'},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
