from rest_framework import serializers
from .models import Category, Product, ProductImage, Review


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description',
            'parent', 'product_count', 'subcategories',
        ]
        read_only_fields = ['slug']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()

    def get_subcategories(self, obj):
        subs = obj.subcategories.all()
        if subs.exists():
            return CategorySerializer(subs, many=True).data
        return []


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'sort_order']


class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    user_name = serializers.ReadOnlyField(source='user.full_name')

    class Meta:
        model = Review
        fields = [
            'id', 'user_email', 'user_name',
            'rating', 'comment', 'created_at',
        ]
        read_only_fields = ['user_email', 'user_name', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """Lighter version for list view - skips nested reviews/images."""
    category_name = serializers.ReadOnlyField(source='category.name')
    seller_name = serializers.ReadOnlyField(source='seller.full_name')
    in_stock = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'compare_at_price',
            'image_url', 'category_name', 'seller_name',
            'in_stock', 'discount_percent', 'avg_rating', 'created_at',
        ]

    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        total = sum(r.rating for r in reviews)
        return round(total / len(reviews), 1)


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer with nested reviews, images, etc."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    seller_name = serializers.ReadOnlyField(source='seller.full_name')
    in_stock = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'compare_at_price',
            'sku', 'stock_quantity', 'category', 'category_id',
            'seller', 'seller_name', 'image_url', 'images',
            'is_active', 'in_stock', 'discount_percent',
            'avg_rating', 'review_count', 'reviews',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['slug', 'seller', 'created_at', 'updated_at']

    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        total = sum(r.rating for r in reviews)
        return round(total / len(reviews), 1)

    def get_review_count(self, obj):
        return len(obj.reviews.all())
