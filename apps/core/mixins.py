from django.utils.functional import cached_property

from apps.core.utils import get_shop_language


class ShopLanguageMixin:
    """Expose active Parler language to class-based views."""

    @cached_property
    def shop_language(self) -> str:
        return get_shop_language(self.request)
