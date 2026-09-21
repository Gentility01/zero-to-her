from rest_framework import mixins, viewsets

from products.api.serializers import ProductSerializer
from products.models import Product, Order
from products.api.serializers import OrderSerializer 






class ProductListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer 
    
class ProductDetailView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductCreateView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
class ProductUpdateView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    

class ProductDeleteView(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



class OrderListCreateView(mixins.ListCreateAPIView):
    """
    this view will allow users to list and create orders. 
    The queryset is filtered to only include orders for the
    currently authenticated user."""
    serializer_class = OrderSerializer
    # NOTE: no class-level 'queryset' attribute at all -- get_queryset() replaces
    def get_queryset(self):
        # self.request is available here -- this runs FRESH for every request,
        # correctly scoped to whoever is actually asking.
        return Order.objects.filter(user=self.request.user)



