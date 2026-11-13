"""
API documentation (schemas) for the user and product endpoints.

drf-spectacular reads these decorators and uses them to build the docs at
/api/docs/ (Swagger) and /api/redoc/.

- tags        -> groups endpoints into sections in the docs
- summary     -> the short title shown next to each endpoint
- description -> longer text shown when you open an endpoint
- examples    -> ready-made request bodies you can try with "Try it out"

Usage in a view:

    @user_schema
    class UserViewSet(viewsets.ModelViewSet):
        ...
"""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers

from products.api.serializers2 import LoginSerializer, UserSerializer

# ---------------------------------------------------------------------------
# Example request bodies
# ---------------------------------------------------------------------------

USER_EXAMPLE = OpenApiExample(
    "New user",
    value={
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret123",
        "first_name": "Test",
        "last_name": "User",
    },
    request_only=True,
)

LOGIN_EXAMPLE = OpenApiExample(
    "Login",
    value={"username": "testuser", "password": "secret123"},
    request_only=True,
)

PRODUCT_EXAMPLE = OpenApiExample(
    "New product",
    value={
        "name": "Laptop",
        "description": "A fast laptop",
        "user": "<user id>",
        "categories": ["<category id>"],
        "price": "999.99",
        "stock": 10,
    },
    request_only=True,
)

PRODUCT_PATCH_EXAMPLE = OpenApiExample(
    "Change price and stock",
    value={"price": "799.99", "stock": 5},
    request_only=True,
)

# ---------------------------------------------------------------------------
# Users  (/api/v2/users/)
# ---------------------------------------------------------------------------

USER_TAG = ["Users Endpoimt"]

user_schema = extend_schema_view(
    list=extend_schema(tags=USER_TAG, summary="List all users"),
    retrieve=extend_schema(tags=USER_TAG, summary="Get one user"),
    create=extend_schema(
        tags=USER_TAG,
        summary="Create a user (sign up)",
        description="The password is stored hashed and is never returned.",
        examples=[USER_EXAMPLE],
    ),
    update=extend_schema(tags=USER_TAG, summary="Replace a user", examples=[USER_EXAMPLE]),
    partial_update=extend_schema(tags=USER_TAG, summary="Change some fields of a user"),
    destroy=extend_schema(tags=USER_TAG, summary="Delete a user"),
)

login_schema = extend_schema(
    tags=USER_TAG,
    summary="Log in",
    description="Send a username (or email) and password. "
    "Returns the user if they are correct.",
    request=LoginSerializer,
    responses={
        200: inline_serializer(
            "LoginResponse",
            {"message": serializers.CharField(), "user": UserSerializer()},
        ),
        400: OpenApiResponse(description="Wrong username/email or password"),
    },
    examples=[LOGIN_EXAMPLE],
)

# ---------------------------------------------------------------------------
# Products v1  (/api/products/)  -- one ViewSet does everything
# ---------------------------------------------------------------------------

PRODUCT_V1_TAG = ["Products (v1)"]

product_v1_schema = extend_schema_view(
    list=extend_schema(
        tags=PRODUCT_V1_TAG,
        summary="List products",
        description="Filter with ?name=, ?categories=<id> or ?is_active=true",
    ),
    retrieve=extend_schema(tags=PRODUCT_V1_TAG, summary="Get one product"),
    create=extend_schema(tags=PRODUCT_V1_TAG, summary="Create a product", examples=[PRODUCT_EXAMPLE]),
    update=extend_schema(tags=PRODUCT_V1_TAG, summary="Replace a product", examples=[PRODUCT_EXAMPLE]),
    partial_update=extend_schema(
        tags=PRODUCT_V1_TAG, summary="Change some fields of a product", examples=[PRODUCT_PATCH_EXAMPLE]
    ),
    destroy=extend_schema(tags=PRODUCT_V1_TAG, summary="Delete a product"),
    low_stock=extend_schema(
        tags=PRODUCT_V1_TAG,
        summary="Check if stock is low",
        description="Says 'Low stock alert!' when stock is below 10.",
        responses=inline_serializer("LowStockResponse", {"message": serializers.CharField()}),
    ),
)

# ---------------------------------------------------------------------------
# Products v2  (/api/v2/products/...)  -- one small view per action
# ---------------------------------------------------------------------------

PRODUCT_V2_TAG = ["Products (v2)"]

product_list_schema = extend_schema_view(
    list=extend_schema(tags=PRODUCT_V2_TAG, summary="List products"),
)
product_detail_schema = extend_schema_view(
    retrieve=extend_schema(tags=PRODUCT_V2_TAG, summary="Get one product"),
)
product_create_schema = extend_schema_view(
    create=extend_schema(tags=PRODUCT_V2_TAG, summary="Create a product", examples=[PRODUCT_EXAMPLE]),
)
product_update_schema = extend_schema_view(
    update=extend_schema(tags=PRODUCT_V2_TAG, summary="Replace a product", examples=[PRODUCT_EXAMPLE]),
    partial_update=extend_schema(
        tags=PRODUCT_V2_TAG, summary="Change some fields of a product", examples=[PRODUCT_PATCH_EXAMPLE]
    ),
)
product_delete_schema = extend_schema_view(
    destroy=extend_schema(tags=PRODUCT_V2_TAG, summary="Delete a product"),
)
