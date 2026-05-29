"""Serbian admin site titles and grouped navigation context."""

from django.contrib import admin

from apps.core.admin_navigation import get_admin_nav_sections
from apps.core.admin_site import patch_admin_site_urls

patch_admin_site_urls()

admin.site.site_header = "Kod Pendule — administracija"
admin.site.site_title = "Kod Pendule admin"
admin.site.index_title = "Upravljanje prodavnicom"

_original_each_context = admin.site.each_context


def _each_context_with_nav(request):
    context = _original_each_context(request)
    if request.path.startswith("/admin"):
        try:
            context["kp_admin_nav_sections"] = get_admin_nav_sections(
                context.get("available_apps", []),
                request,
            )
        except Exception:
            import logging

            logging.getLogger(__name__).exception(
                "Failed to build admin navigation sections",
            )
            context["kp_admin_nav_sections"] = []
    return context


admin.site.each_context = _each_context_with_nav

_original_index = admin.site.index


def _index_with_home(request, extra_context=None):
    from apps.core.admin_home import build_admin_home_context

    context = {
        **build_admin_home_context(request),
        **(extra_context or {}),
    }
    return _original_index(request, extra_context=context)


admin.site.index = _index_with_home
