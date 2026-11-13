from django.contrib import admin
from django.contrib.auth.hashers import identify_hasher, make_password

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_active", "date_joined")

    def save_model(self, request, obj, form, change):
        # hash the password if it was typed in as plain text
        try:
            identify_hasher(obj.password)
        except ValueError:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)
