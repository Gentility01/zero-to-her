from rest_framework import viewsets

from rest_framework.decorators import action
from rest_framework.response import Response

from products.api.serializers import (
    CategoryCreateUpdateSerializer,
    CategoryDetailSerializer,
    CategoryListSerializer, 
    ProductCreateUpdateSerializer, 
    ProductSerializer
)
from products.api.schemas import product_v1_schema
from products.models import Product, Category

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name", "is_active"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CategoryDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CategoryCreateUpdateSerializer
        return super().get_serializer_class()
    
    
@product_v1_schema
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name", "categories", "is_active"]

    def get_serializer_class(self):
        
        if self.action == "retrieve":
            return ProductSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return super().get_serializer_class()
    
    @action(detail=True, methods=["get"], url_path="low-stock")
    def low_stock(self, request, pk=None):
        product = self.get_object()
        if product.stock < 10:
            return Response({"message": "Low stock alert!"})
        return Response({"message": "Stock level is sufficient."})