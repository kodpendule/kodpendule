from django import template

from apps.core.storefront_urls import shop_reverse

register = template.Library()


@register.simple_tag
def shop_url(viewname, *args, **kwargs):
    """Reverse a storefront route in the active UI language."""
    return shop_reverse(viewname, **kwargs)
