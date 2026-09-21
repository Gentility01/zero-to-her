from django.contrib import admin
from .models import Product, Category, Order

# Register your models here.

class CategoryInline(admin.TabularInline):
    model = Product.categories.through
    extra = 1
    verbose_name = "Category"
    verbose_name_plural = "Categories"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [CategoryInline]
    list_display = (
        "id", 
        "name", 
        "user", 
        "price", 
        "stock", 
        "is_active", 
        "in_sale", 
        "created_at", 
        "updated_at",
        "get_category_count",
    )
    list_filter = ("is_active", "in_sale", "created_at", "updated_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)
    filter_horizontal = ("categories",)
    readonly_fields = ("id", "price", "created_at", "updated_at", "get_category_count")

    @admin.display(description='Category Count')
    def get_category_count(self, obj):
            return obj.categories.count()
        # get_category_count.short_description = 'Category Count'
    
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = (
#         "id", 
#         "name", 
#         "slug", 
#         "order", 
#         "is_active", 
#         "created_at", 
#         "updated_at"
#     )
#     list_filter = ("is_active", "created_at", "updated_at")
#     search_fields = ("name", "description")
#     ordering = ("order",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Main Informations", {
            "fields": ("user", "products", "total_price", "is_active")
        }),
    )
    
    # readonly_fields = ("id", "user", "products", "total_price", "created_at", "updated_at")
    