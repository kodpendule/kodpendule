from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from apps.core.storefront_urls import shop_reverse, shop_reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from apps.accounts.forms import LoginForm, RegistrationForm


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        return shop_reverse("orders:history")


class UserRegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegistrationForm
    success_url = shop_reverse_lazy("orders:history")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.redirect_authenticated()
        return super().dispatch(request, *args, **kwargs)

    def redirect_authenticated(self):
        from django.shortcuts import redirect

        return redirect(self.success_url)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request,
            _("Welcome, %(name)s! Your account has been created.")
            % {"name": user.get_short_name() or user.username},
        )
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    next_page = shop_reverse_lazy("core:home")

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == "POST":
            messages.info(request, _("You have been signed out."))
        return response
