from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from apps.cart.cart import get_cart
from apps.checkout.forms import CheckoutForm
from apps.core.mixins import ShopLanguageMixin
from apps.orders.services import CheckoutError, create_order_from_checkout
from apps.shipping.selectors import active_cities


class CheckoutView(ShopLanguageMixin, FormView):
    template_name = "checkout/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("checkout:success")

    def dispatch(self, request, *args, **kwargs):
        cart = get_cart(request)
        if cart.is_empty:
            messages.warning(request, _("Your cart is empty."))
            return redirect("products:list")
        if not active_cities().exists():
            messages.error(
                request,
                _("Delivery is not available yet. Please contact us."),
            )
            return redirect("core:contact")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        if user.is_authenticated:
            initial.setdefault("first_name", user.first_name)
            initial.setdefault("last_name", user.last_name)
            initial.setdefault("guest_email", user.email or "")
            profile = getattr(user, "profile", None)
            if profile:
                initial.setdefault("phone", profile.phone)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        lines = cart.get_lines()
        for line in lines:
            line.product.set_current_language(self.shop_language)
        cities = list(active_cities())
        context.update(
            {
                "cart_lines": lines,
                "cart_subtotal": cart.subtotal,
                "cities": cities,
                "city_prices": {str(c.pk): str(c.shipping_price) for c in cities},
                "is_guest": not self.request.user.is_authenticated,
                "meta_title": _("Checkout"),
                "canonical_url": self.request.build_absolute_uri(),
            }
        )
        return context

    def form_valid(self, form):
        cart = get_cart(self.request)
        try:
            order = create_order_from_checkout(
                cart=cart,
                user=self.request.user,
                guest_email=form.cleaned_data["guest_email"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                phone=form.cleaned_data["phone"],
                shipping_city=form.cleaned_data["shipping_city"],
                shipping_street=form.cleaned_data["shipping_street"],
                shipping_postal_code=form.cleaned_data["shipping_postal_code"],
                billing_street=form.cleaned_data["billing_street"],
                billing_city_name=form.cleaned_data["billing_city_name"],
                billing_postal_code=form.cleaned_data["billing_postal_code"],
                order_notes=form.cleaned_data["order_notes"],
                delivery_date=form.cleaned_data.get("delivery_date"),
                flexible_delivery=form.cleaned_data.get("flexible_delivery", False),
            )
        except CheckoutError as exc:
            messages.error(self.request, exc.message)
            return self.form_invalid(form)

        self.request.session["last_order_number"] = order.order_number
        messages.success(
            self.request,
            _("Thank you! Your order %(number)s has been placed.")
            % {"number": order.order_number},
        )
        return super().form_valid(form)


class CheckoutSuccessView(ShopLanguageMixin, TemplateView):
    template_name = "checkout/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = self.request.session.pop("last_order_number", None)
        context.update(
            {
                "order_number": order_number,
                "meta_title": _("Order confirmed"),
                "canonical_url": self.request.build_absolute_uri(),
            }
        )
        return context
