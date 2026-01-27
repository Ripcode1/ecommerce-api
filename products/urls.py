from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    # review create has to come before router, otherwise the @action on
    # ProductViewSet catches the POST and returns 403 (seller-only permission)
    path('products/<slug:product_slug>/reviews/', views.ReviewCreateView.as_view(), name='product-review-create'),
    path('', include(router.urls)),
]
