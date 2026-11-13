import uuid

from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from products.api.serializers2 import (
    LoginSerializer,
    OrderSerializer,
    ProductSerializer,
    UserSerializer,
)
from products.api.schemas import (
    login_schema,
    product_create_schema,
    product_delete_schema,
    product_detail_schema,
    product_list_schema,
    product_update_schema,
    user_schema,
)
from products.models import Order, Product
from user.models import User


# GET    /api/v2/products/                   -> list all products
# GET    /api/v2/products/<id>/              -> one product
# POST   /api/v2/products/create/            -> create a product
# PUT    /api/v2/products/<id>/update/       -> full update
# PATCH  /api/v2/products/<id>/update/       -> partial update
# DELETE /api/v2/products/<id>/delete/       -> delete a product

@product_list_schema
class ProductListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.prefetch_related("categories")
    serializer_class = ProductSerializer


@product_detail_schema
class ProductDetailView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.prefetch_related("categories")
    serializer_class = ProductSerializer


@product_create_schema
class ProductCreateView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


@product_update_schema
class ProductUpdateView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


@product_delete_schema
class ProductDeleteView(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v2/orders/              -> list orders
    GET  /api/v2/orders/?user=<id>    -> list orders for one user
    POST /api/v2/orders/              -> create an order

    Products and orders point at the custom ``user.User`` model, not Django's
    auth user, so ``request.user`` can't be used to scope the queryset. Pass
    ``?user=<id>`` instead.
    """
    serializer_class = OrderSerializer

    def get_queryset(self):
        # runs fresh for every request
        queryset = Order.objects.select_related("user").prefetch_related(
            "order_items__product"
        )
        user_id = self.request.query_params.get("user")
        if user_id:
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                raise ValidationError({"user": "Must be a valid user id (UUID)."})
            queryset = queryset.filter(user_id=user_id)
        return queryset


class OrderDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/v2/orders/<id>/   -> one order
    DELETE /api/v2/orders/<id>/   -> delete an order
    """
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related("user").prefetch_related("order_items__product")


@user_schema
class UserViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for users at /api/v2/users/ -- you need a user id to create
    products and orders.
    """
    queryset = User.objects.all().order_by("date_joined")
    serializer_class = UserSerializer

    @login_schema
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        """
        POST /api/v2/users/login/
        {"username": "<username or email>", "password": "..."}
        Returns the user's details if the credentials are correct, otherwise 400.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return Response(
            {"message": "Login successful.", "user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )
