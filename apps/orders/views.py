from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView

from apps.core.mixins import ShopLanguageMixin
from apps.orders.forms import GuestOrderTrackForm
from apps.orders.models import Order
from apps.orders.selectors.order_selectors import (
    get_order_for_guest_tracking,
    order_detail_qs,
    orders_for_user,
)
from apps.orders.services.order_access import grant_order_access, user_can_view_order
from apps.orders.status_display import order_status_context


class GuestOrderTrackView(ShopLanguageMixin, FormView):
    """Guest order lookup by order number and email (same error for any mismatch)."""

    template_name = "orders/track.html"
    form_class = GuestOrderTrackForm

    def get_initial(self):
        initial = super().get_initial()
        order_number = self.request.GET.get("order_number", "").strip()
        if order_number:
            initial["order_number"] = order_number
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "meta_title": _("Track your order"),
                "canonical_url": self.request.build_absolute_uri(),
            }
        )
        return context

    def form_valid(self, form):
        order = get_order_for_guest_tracking(
            form.cleaned_data["order_number"],
            form.cleaned_data["email"],
        )
        if order is None:
            form.add_error(
                None,
                _(
                    "We could not find an order with these details. "
                    "Check the order number and email, then try again."
                ),
            )
            return self.form_invalid(form)
        grant_order_access(self.request, order)
        return redirect("orders:detail", order_number=order.order_number)


class OrderDetailView(ShopLanguageMixin, DetailView):
    """Order detail for guests (after track/checkout) or logged-in owners."""

    model = Order
    template_name = "orders/detail.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"

    def get_queryset(self):
        return order_detail_qs()

    def get_object(self, queryset=None):
        order = super().get_object(queryset)
        if not user_can_view_order(self.request, order):
            raise Http404
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context["order"]
        context.update(
            {
                "meta_title": _("Order %(number)s")
                % {"number": order.order_number},
                "canonical_url": self.request.build_absolute_uri(),
                **order_status_context(order.status),
            }
        )
        return context


class OrderHistoryView(LoginRequiredMixin, ShopLanguageMixin, ListView):
    """Logged-in customer order list."""

    template_name = "orders/history.html"
    context_object_name = "orders"
    paginate_by = 15

    def get_queryset(self):
        return orders_for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "meta_title": _("My orders"),
                "canonical_url": self.request.build_absolute_uri(),
            }
        )
        return context
