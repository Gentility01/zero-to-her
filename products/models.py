from django.db import models
import uuid
from django.db.models import F
from django.db import transaction
# Create your models here.
# One to one relationship with User model 
# one to many relationship with Product model(ForeignKey)
# many to many relationship with Category model


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="A unique identifier for the category, used in URLs.")
    description = models.TextField()
    order = models.PositiveIntegerField(
        default=0, null=True, blank=True,
        help_text="The order in which the category should be displayed. Lower numbers will be displayed first."
     )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='products')
    slug = models.SlugField(max_length=100, unique=True, help_text="A unique identifier for the product, used in URLs.")
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name='products')
    order = models.PositiveIntegerField(
        default=0, null=True, blank=True,
        help_text="The order in which the product should be displayed. Lower numbers will be displayed first."
     )
    stock = models.PositiveIntegerField(default=0)
    sold_out = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    is_active = models.BooleanField(default=True)
    in_sale = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:

        indexes = [

            # Speeds up: Order.objects.filter(user=x, status='PENDING')

            models.Index(

                fields=['user', 'price', 'created_at', "updated_at"],

                name='product_indexing',

            ),

        ]
    
    def __str__(self):
        return self.name
    
    def subtract_stock(self):
        Product.objects.filter(id=self.id).update(
            stock=F("stock") - 1
        )
    
class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
    
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    @transaction.atomic
    def create_order(user, cart_items):
        order = Order.objects.create(user=user, status='PENDING')
        for item in cart_items:
            OrderItem.objects.create(
                    order=order, product=item.product, quantity=item.quantity
                )
        # If we reach here, EVERYTHING above committed together.
        # If any line inside raised an exception, NONE of it was saved.
        return order