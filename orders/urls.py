from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    # this has to come before the router, otherwise 'place' gets matched as a pk
    path('orders/place/', views.PlaceOrderView.as_view(), name='place-order'),
    path('', include(router.urls)),
]
