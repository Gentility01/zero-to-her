from rest_framework import serializers 
from products.models import Product, Category
from products.api.serializers2 import unique_product_slug


class CategoryListSerializer(serializers.ModelSerializer):
    """
        Serializer for listing categories. It includes the basic fields of the Category model.
    """
    
    class Meta:
        model = Category
        fields = ["id", "name", "description"]
        
class CategoryDetailSerializer(serializers.ModelSerializer):
    """
        Serializer for detailed view of a category. It includes all fields of the Category model and a
        nested list of products associated with the category.
    """
    
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "products"]

    def get_products(self, obj) -> list[dict]:
        products = obj.products.all()
        return ProductSerializer(products, many=True).data
    
class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
        Serializer for creating and updating categories. It includes all fields of the Category model.
    """
    
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "order", "is_active"]
        read_only_fields = ["id"]


class CategorySerializer(serializers.ModelSerializer):
    """
        Serializer for the Category model. It includes all fields of the Category model.
    """
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "order", "is_active"]
        read_only_fields = ["id"]
    
class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model. It includes all fields of the Product model and additional computed fields.
    the serializer methods helps us to get the category 
    name, total product count, stock status, and ownership status of the product.
    """
    
    category_name = serializers.SerializerMethodField()
    total_product_count = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

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
            "total_product_count",
            "category_name",
            "is_in_stock",
            "is_owner",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "price": {"min_value": 0},
            "stock": {"required": False},
        }

    def get_total_product_count(self, obj) -> int:
        return Product.objects.count()

    def get_category_name(self, obj) -> list[str]:
        # 'obj' is the actual Product instance being serialized
        return [category.name for category in obj.categories.all()]

    def get_is_in_stock(self, obj) -> bool:
        return obj.stock > 0

    def get_is_owner(self, obj) -> bool:
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return False
        return obj.user_id == request.user.id 
    


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products. It includes all fields of the Product model.
    """
    
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "user",
            "description",
            "categories",
            "order",
            "stock",
            "sold_out",
            "price",
            "is_active",
            "in_sale",
        ]
        read_only_fields = ["id", "slug"]
        extra_kwargs = {
            "price": {"min_value": 0},
            "categories": {"required": False},
        }

    def create(self, validated_data):
        # slug is unique and required in the database, so build it from the name
        validated_data["slug"] = unique_product_slug(validated_data["name"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "name" in validated_data and validated_data["name"] != instance.name:
            validated_data["slug"] = unique_product_slug(validated_data["name"], instance)
        return super().update(instance, validated_data)
        
        
class ProductRetrieveSerializer(ProductSerializer):
    """
    Serializer for retrieving a product. 
    It includes all fields of the Product model and additional computed fields.
    """
