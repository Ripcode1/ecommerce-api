"""
Quick way to populate the db with some test data.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product, Review

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample products and categories'

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # two sellers so the data looks less empty
        seller, created = User.objects.get_or_create(
            email='seller@store.com',
            defaults={
                'username': 'store_seller',
                'first_name': 'James',
                'last_name': 'Mitchell',
                'is_seller': True,
            }
        )
        if created:
            seller.set_password('DemoSeller123!')
            seller.save()
            self.stdout.write(f"  Created seller: {seller.email}")

        seller2, created = User.objects.get_or_create(
            email='tech@store.com',
            defaults={
                'username': 'tech_seller',
                'first_name': 'Thabo',
                'last_name': 'Ndlovu',
                'is_seller': True,
            }
        )
        if created:
            seller2.set_password('DemoSeller123!')
            seller2.save()
            self.stdout.write(f"  Created seller: {seller2.email}")

        # buyer so we can seed some reviews
        buyer, created = User.objects.get_or_create(
            email='buyer@test.com',
            defaults={
                'username': 'test_buyer',
                'first_name': 'Sarah',
                'last_name': 'Coetzee',
            }
        )
        if created:
            buyer.set_password('DemoBuyer123!')
            buyer.save()
            self.stdout.write(f"  Created buyer: {buyer.email}")

        # categories
        cat_list = [
            ('Electronics', 'Phones, laptops, gadgets and accessories'),
            ('Clothing', 'Mens and womens apparel'),
            ('Home & Kitchen', 'Furniture, appliances, and home decor'),
            ('Books', 'Fiction, non-fiction, and educational'),
            ('Sports', 'Equipment and gear'),
        ]

        cats = {}
        for name, desc in cat_list:
            obj, created = Category.objects.get_or_create(
                name=name, defaults={'description': desc}
            )
            cats[name] = obj
            if created:
                self.stdout.write(f"  Category: {name}")

        products = [
            # electronics
            {
                'name': 'Wireless Bluetooth Headphones',
                'description': 'Over-ear with noise cancellation and 30hr battery.',
                'price': 79.99,
                'compare_at_price': 99.99,
                'sku': 'ELEC-001',
                'stock_quantity': 45,
                'category': cats['Electronics'],
                'seller': seller,
            },
            {
                'name': 'USB-C Charging Cable 2m',
                'description': 'Braided nylon, fast charging support.',
                'price': 12.99,
                'sku': 'ELEC-002',
                'stock_quantity': 200,
                'category': cats['Electronics'],
                'seller': seller,
            },
            {
                'name': 'Portable Bluetooth Speaker',
                'description': 'Waterproof, 12hr battery. Pretty loud for its size.',
                'price': 44.99,
                'compare_at_price': 59.99,
                'sku': 'ELEC-003',
                'stock_quantity': 35,
                'category': cats['Electronics'],
                'seller': seller2,
            },
            {
                'name': 'Wireless Phone Charger',
                'description': '15W fast charging pad. Works with any Qi phone.',
                'price': 22.50,
                'sku': 'ELEC-004',
                'stock_quantity': 90,
                'category': cats['Electronics'],
                'seller': seller2,
            },
            {
                'name': 'Laptop Stand Aluminium',
                'description': 'Adjustable height, fits up to 17 inch. Folds flat.',
                'price': 38.99,
                'sku': 'ELEC-005',
                'stock_quantity': 3,  # low stock to trigger celery alert
                'category': cats['Electronics'],
                'seller': seller,
            },

            # clothing
            {
                'name': 'Slim Fit Denim Jacket',
                'description': 'Medium wash, sizes S to XL.',
                'price': 64.50,
                'compare_at_price': 85.00,
                'sku': 'CLO-001',
                'stock_quantity': 30,
                'category': cats['Clothing'],
                'seller': seller,
            },
            {
                'name': 'Cotton Crew Neck T-Shirt',
                'description': 'Organic cotton. Black, white, grey, navy.',
                'price': 18.99,
                'sku': 'CLO-002',
                'stock_quantity': 150,
                'category': cats['Clothing'],
                'seller': seller,
            },
            {
                'name': 'Running Shorts',
                'description': 'Quick dry with zip pocket.',
                'price': 27.99,
                'sku': 'CLO-003',
                'stock_quantity': 75,
                'category': cats['Clothing'],
                'seller': seller2,
            },

            # home & kitchen
            {
                'name': 'Stainless Steel Water Bottle 750ml',
                'description': 'Double wall insulated. Cold 24hrs, hot 12hrs.',
                'price': 24.99,
                'sku': 'HOME-001',
                'stock_quantity': 80,
                'category': cats['Home & Kitchen'],
                'seller': seller,
            },
            {
                'name': 'Non-Stick Frying Pan 28cm',
                'description': 'Ceramic coated, works on induction too.',
                'price': 34.99,
                'sku': 'HOME-002',
                'stock_quantity': 40,
                'category': cats['Home & Kitchen'],
                'seller': seller,
            },
            {
                'name': 'French Press Coffee Maker 1L',
                'description': 'Glass with stainless steel filter. Makes good coffee.',
                'price': 29.99,
                'sku': 'HOME-003',
                'stock_quantity': 55,
                'category': cats['Home & Kitchen'],
                'seller': seller2,
            },

            # books
            {
                'name': 'Python Crash Course 3rd Edition',
                'description': 'Hands-on intro to programming. Good for beginners.',
                'price': 39.99,
                'sku': 'BOOK-001',
                'stock_quantity': 25,
                'category': cats['Books'],
                'seller': seller,
            },
            {
                'name': 'Clean Code',
                'description': 'Robert Martin. Every dev should probably read this.',
                'price': 34.99,
                'sku': 'BOOK-002',
                'stock_quantity': 18,
                'category': cats['Books'],
                'seller': seller,
            },

            # sports
            {
                'name': 'Yoga Mat 6mm',
                'description': 'Non-slip with carrying strap.',
                'price': 29.99,
                'sku': 'SPRT-001',
                'stock_quantity': 60,
                'category': cats['Sports'],
                'seller': seller2,
            },
            {
                'name': 'Resistance Bands Set',
                'description': '5 bands light to heavy. Comes with a door anchor.',
                'price': 19.99,
                'sku': 'SPRT-002',
                'stock_quantity': 100,
                'category': cats['Sports'],
                'seller': seller2,
            },
            {
                'name': 'Skipping Rope Adjustable',
                'description': 'Ball bearing handles, adjustable length.',
                'price': 14.99,
                'sku': 'SPRT-003',
                'stock_quantity': 120,
                'category': cats['Sports'],
                'seller': seller,
            },
        ]

        created_products = []
        for data in products:
            obj, was_created = Product.objects.get_or_create(
                sku=data['sku'],
                defaults=data,
            )
            if was_created:
                self.stdout.write(f"  Product: {obj.name}")
                created_products.append(obj)

        # drop a few reviews so avg_rating actually shows something
        review_data = [
            ('ELEC-001', buyer, 5, 'Really solid, battery lasts forever'),
            ('ELEC-003', buyer, 4, 'Good sound but takes a while to pair'),
            ('CLO-001', buyer, 5, 'Fits perfectly'),
            ('HOME-003', buyer, 3, 'Decent but the filter lets some grounds through'),
            ('BOOK-001', buyer, 5, 'Got me into python'),
            ('SPRT-001', buyer, 4, 'Good grip, doesnt slide on tile floors'),
        ]

        for sku, user, rating, comment in review_data:
            try:
                product = Product.objects.get(sku=sku)
                Review.objects.get_or_create(
                    product=product,
                    user=user,
                    defaults={'rating': rating, 'comment': comment},
                )
            except Product.DoesNotExist:
                pass

        total = Product.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Done! {total} products in the db."))
