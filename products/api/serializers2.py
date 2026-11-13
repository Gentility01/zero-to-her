from django.contrib.auth.hashers import (
    check_password,
    identify_hasher,
    is_password_usable,
    make_password,
)
from django.db import transaction
from django.db.models import F
from django.utils.text import slugify
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from products.models import Category, Order, OrderItem, Product
from user.models import User


def unique_product_slug(name, instance=None):
    """Build a slug from the name and add a suffix if it is already taken."""
    base = slugify(name)[:90] or "product"
    slug = base
    counter = 1
    qs = Product.objects.all()
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(slug=slug).exists():
        counter += 1
        slug = f"{base}-{counter}"
    return slug


class UserSerializer(serializers.ModelSerializer):
    # password can be sent in, but is never returned in a response
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):
    # log in with either the username or the email
    username = serializers.CharField(help_text="Username or email")
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        login = attrs["username"]
        password = attrs["password"]
        user = User.objects.filter(username=login).first() or User.objects.filter(
            email__iexact=login
        ).first()

        if user is None or not self._password_matches(user, password):
            raise serializers.ValidationError("Invalid username/email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is disabled.")
        attrs["user"] = user
        return attrs

    @staticmethod
    def _password_matches(user, password):
        if is_password_usable(user.password) and identify_hasher_safe(user.password):
            return check_password(password, user.password)
        # old users created in the admin have plain-text passwords:
        # accept them once, then store a proper hash
        if user.password == password:
            user.password = make_password(password)
            user.save(update_fields=["password"])
            return True
        return False


def identify_hasher_safe(encoded):
    try:
        identify_hasher(encoded)
        return True
    except ValueError:
        return False


@extend_schema_serializer(component_name="ProductV2")
class ProductSerializer(serializers.ModelSerializer):
    # write: send a list of category ids, e.g. "categories": ["<uuid>", "<uuid>"]
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )
    # write: send the id of an existing user, e.g. "user": "<uuid>"
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    slug = serializers.SlugField(read_only=True)

    total_product_count = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "user",
            "description",
            "categories",
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

    # NOTE: these methods must live on the serializer class, not inside Meta
    def get_total_product_count(self, obj) -> int:
        return Product.objects.count()

    def get_category_name(self, obj) -> list[str]:
        # a product can have many categories, so return all of their names
        return [category.name for category in obj.categories.all()]

    def get_is_in_stock(self, obj) -> bool:
        return obj.stock > 0

    def get_is_owner(self, obj) -> bool:
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return str(obj.user_id) == str(request.user.pk)

    def create(self, validated_data):
        validated_data["slug"] = unique_product_slug(validated_data["name"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "name" in validated_data and validated_data["name"] != instance.name:
            validated_data["slug"] = unique_product_slug(validated_data["name"], instance)
        return super().update(instance, validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity"]
        read_only_fields = ["id"]
        extra_kwargs = {"quantity": {"min_value": 1}}


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_email = serializers.CharField(source="user.email", read_only=True)
    items = OrderItemSerializer(source="order_items", many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_email",
            "items",
            "total_price",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_total_price(self, obj) -> str:
        return str(sum(item.product.price * item.quantity for item in obj.order_items.all()))

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("An order needs at least one item.")
        # add up quantities in case the same product is listed twice
        wanted = {}
        for item in items:
            product = item["product"]
            wanted[product] = wanted.get(product, 0) + item["quantity"]
        for product, quantity in wanted.items():
            if not product.is_active:
                raise serializers.ValidationError(f"'{product.name}' is not available.")
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Only {product.stock} of '{product.name}' left in stock."
                )
        return items

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop("order_items")
        order = Order.objects.create(**validated_data)
        for item in items:
            OrderItem.objects.create(order=order, **item)
            Product.objects.filter(pk=item["product"].pk).update(
                stock=F("stock") - item["quantity"]
            )
        order.products.set({item["product"] for item in items})
        return order


class DashboardSummarySerializer(serializers.Serializer):
    total_orders_today = serializers.IntegerField()
    total_revenue_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    low_stock_product_count = serializers.IntegerField()
    # No Meta class at all -- nothing here is 'generated from a model'
