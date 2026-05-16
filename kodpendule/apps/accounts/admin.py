from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from apps.accounts.models import Address, CustomerProfile, User


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    extra = 0


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = (
        "address_type",
        "label",
        "street_line_1",
        "city",
        "postal_code",
        "is_default",
    )


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    inlines = [CustomerProfileInline, AddressInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "address_type", "city", "is_default")
    list_filter = ("address_type", "is_default")
    search_fields = ("user__username", "user__email", "city", "street_line_1")
    list_select_related = ("user",)
