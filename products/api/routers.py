from django.urls import path
from rest_framework.routers import DefaultRouter

from products.api import views2
from products.api.views import CategoryViewSet, ProductViewSet

# ---- v1: ModelViewSets, all actions on one URL ----
router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"v2/users", views2.UserViewSet, basename="v2-user")

# ---- v2: one small view per action ----
# Each view only handles one action, so each needs its own URL.
v2_urlpatterns = [
    path(
        "v2/products/",
        views2.ProductListView.as_view({"get": "list"}),
        name="v2-product-list",
    ),
    path(
        "v2/products/create/",
        views2.ProductCreateView.as_view({"post": "create"}),
        name="v2-product-create",
    ),
    path(
        "v2/products/<uuid:pk>/",
        views2.ProductDetailView.as_view({"get": "retrieve"}),
        name="v2-product-detail",
    ),
    path(
        "v2/products/<uuid:pk>/update/",
        views2.ProductUpdateView.as_view({"put": "update", "patch": "partial_update"}),
        name="v2-product-update",
    ),
    path(
        "v2/products/<uuid:pk>/delete/",
        views2.ProductDeleteView.as_view({"delete": "destroy"}),
        name="v2-product-delete",
    ),
    path("v2/orders/", views2.OrderListCreateView.as_view(), name="v2-order-list"),
    path("v2/orders/<uuid:pk>/", views2.OrderDetailView.as_view(), name="v2-order-detail"),
]

urlpatterns = v2_urlpatterns + router.urls
