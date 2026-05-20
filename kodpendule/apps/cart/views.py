from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from apps.cart.cart import get_cart
from apps.core.mixins import ShopLanguageMixin
from apps.core.utils import get_shop_language
from apps.products.models import Product
from apps.products.selectors import get_product_by_slug


class CartDetailView(ShopLanguageMixin, TemplateView):
    template_name = "cart/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        lines = cart.get_lines()
        for line in lines:
            line.product.set_current_language(self.shop_language)
        context.update(
            {
                "cart_lines": lines,
                "cart_subtotal": cart.subtotal,
                "cart_item_count": cart.total_items,
                "meta_title": _("Cart"),
                "canonical_url": self.request.build_absolute_uri(),
            }
        )
        return context


class CartAddView(View):
    """POST: add product to cart."""

    def post(self, request, *args, **kwargs):
        cart = get_cart(request)
        product = None
        if "product_id" in request.POST:
            product = get_object_or_404(
                Product.objects.filter(is_active=True),
                pk=request.POST.get("product_id"),
            )
        elif "slug" in kwargs:
            product = get_product_by_slug(kwargs["slug"])
            if product is None:
                raise Http404

        if product is None:
            messages.error(request, _("Product not found."))
            return redirect("products:list")

        if product.stock < 1:
            messages.error(request, _("This product is out of stock."))
            return redirect(product.get_absolute_url())

        try:
            qty = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            qty = 1
        qty = max(1, qty)

        try:
            cart.add(product, qty)
        except ValueError:
            messages.error(request, _("Not enough items in stock."))
            return redirect(product.get_absolute_url())

        product.set_current_language(get_shop_language(request))
        messages.success(
            request,
            _("“%(name)s” added to cart.")
            % {"name": product.safe_translation_getter("name", any_language=True)},
        )
        next_url = request.POST.get("next") or reverse("cart:detail")
        return HttpResponseRedirect(next_url)


class CartUpdateView(View):
    def post(self, request, *args, **kwargs):
        cart = get_cart(request)
        product = get_object_or_404(
            Product.objects.filter(is_active=True),
            pk=kwargs["product_id"],
        )
        try:
            qty = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            qty = 1
        try:
            cart.set_quantity(product, qty)
            messages.success(request, _("Cart updated."))
        except ValueError:
            messages.error(request, _("Not enough items in stock."))
        return redirect("cart:detail")


class CartRemoveView(View):
    def post(self, request, *args, **kwargs):
        cart = get_cart(request)
        product = get_object_or_404(Product, pk=kwargs["product_id"])
        cart.remove(product)
        messages.info(request, _("Item removed from cart."))
        return redirect("cart:detail")
