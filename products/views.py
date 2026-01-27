from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404

from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ReviewSerializer,
)
from .filters import ProductFilter
from .tasks import notify_low_stock


class IsSellerOrReadOnly(permissions.BasePermission):
    """Only sellers can create/edit, everyone else is read-only."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_seller

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # make sure the seller owns this product
        return obj.seller == request.user


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    @method_decorator(cache_page(60 * 15))  # categories dont change much
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        'category', 'seller'
    ).prefetch_related('reviews', 'images')
    permission_classes = [IsSellerOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'name', 'stock_quantity']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # regular users should only see active products
        if not (self.request.user.is_authenticated and self.request.user.is_seller):
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        product = serializer.save(seller=self.request.user)
        # kick off a background check if stock is low
        if product.stock_quantity < 5:
            try:
                notify_low_stock.delay(product.id)
            except Exception:
                pass

    def perform_update(self, serializer):
        product = serializer.save()
        if product.stock_quantity < 5:
            try:
                notify_low_stock.delay(product.id)
            except Exception:
                pass

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        product = self.get_object()
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class ReviewCreateView(generics.CreateAPIView):
    """Post a review for a product."""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)

        # dont let the same user review twice
        if Review.objects.filter(product=product, user=self.request.user).exists():
            raise ValidationError(
                {'detail': 'You already reviewed this product.'}
            )

        serializer.save(product=product, user=self.request.user)
