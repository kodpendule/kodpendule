from __future__ import annotations

import logging

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from apps.cart.cart import get_cart
from apps.checkout.forms import CheckoutForm
from apps.core.checkout_settings import CheckoutSettings
from apps.core.mixins import ShopLanguageMixin
from apps.core.storefront_urls import shop_reverse, shop_reverse_lazy
from apps.core.utils import activate_parler_language
from apps.orders.selectors import order_detail_qs
from apps.orders.services import (
    CheckoutError,
    create_order_from_checkout,
    notify_customer_new_order,
    notify_staff_new_order,
)
from apps.orders.services.order_access import grant_order_access
from apps.shipping.selectors import active_cities

logger = logging.getLogger(__name__)


class CheckoutView(ShopLanguageMixin, FormView):
    template_name = "checkout/checkout.html"
    form_class = CheckoutForm
    success_url = shop_reverse_lazy("checkout:success")

    def dispatch(self, request, *args, **kwargs):
        cart = get_cart(request)
        if cart.is_empty:
            messages.warning(request, _("Your cart is empty."))
            return redirect(shop_reverse("products:list"))
        if not active_cities().exists():
            messages.error(
                request,
                _("Delivery is not available yet. Please contact us."),
            )
            return redirect(shop_reverse("core:contact"))
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

    def _checkout_shipping_context(self) -> dict:
        settings = CheckoutSettings.load()
        threshold = settings.free_shipping_threshold
        discounted = settings.discounted_shipping_price
        return {
            "free_shipping_threshold": str(threshold) if threshold else "",
            "discounted_shipping_price": str(discounted) if discounted is not None else "",
            "threshold_shipping_mode": settings.threshold_shipping_mode,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        lines = cart.get_lines()
        for line in lines:
            activate_parler_language(line.product, self.shop_language)
        cities = list(active_cities())
        context.update(
            {
                "cart_lines": lines,
                "cart_subtotal": cart.subtotal,
                "cities": cities,
                "city_prices": {str(c.pk): str(c.shipping_price) for c in cities},
                "checkout_shipping": self._checkout_shipping_context(),
                "is_guest": not self.request.user.is_authenticated,
                "meta_title": _("Checkout"),
                "canonical_url": self.request.build_absolute_uri(),
            }
        )
        return context

    def get_success_url(self):
        return shop_reverse("checkout:success", language=self.shop_language)

    def form_invalid(self, form):
        if form.errors:
            messages.error(
                self.request,
                _("Please correct the highlighted fields and try again."),
            )
        return super().form_invalid(form)

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
                order_notes=form.cleaned_data["order_notes"],
            )
        except CheckoutError as exc:
            messages.error(self.request, exc.message)
            return self.render_to_response(self.get_context_data(form=form))
        except Exception:
            logger.exception("Unexpected checkout failure")
            messages.error(
                self.request,
                _("We could not place your order. Please try again or contact us."),
            )
            return self.render_to_response(self.get_context_data(form=form))

        self.request.session["last_order_number"] = order.order_number
        self.request.session["last_order_id"] = order.pk
        grant_order_access(self.request, order)
        notify_customer_new_order(order)
        notify_staff_new_order(order)
        logger.info("Order placed: %s", order.order_number)
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
        order_id = self.request.session.pop("last_order_id", None)
        order = None
        if order_id:
            order = order_detail_qs().filter(pk=order_id).first()
        context.update(
            {
                "order_number": order_number,
                "order": order,
                "meta_title": _("Order confirmed"),
                "canonical_url": self.request.build_absolute_uri(),
            }
        )
        return context
