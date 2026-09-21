from rest_framework import serializers

from products.models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "stock",
            "sold_out",
            "price",
            "is_active",
            "in_sale",
            "created_at",
            "updated_at",
        ]
        
        read_only_fields = ["id", "created_at", "updated_at"]
        

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "product",
            "quantity",
            "status",
            "created_at",
            "updated_at",
        ]
        
        read_only_fields = ["id", "created_at", "updated_at"]