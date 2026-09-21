from django.shortcuts import render
from .models import Product

# Create your views here.


def dashboard(request, product_id):
    product = Product.objects.get(id=product_id)
    product.subtract_stock()
    return render(request, "products/dashboard.html")