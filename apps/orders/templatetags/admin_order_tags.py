from django.contrib.admin.templatetags.admin_list import result_list as django_result_list
from django.contrib.admin.templatetags.base import InclusionAdminNode
from django.template import Library

register = Library()


@register.filter
def at_index(sequence, position):
    if not sequence:
        return None
    try:
        return sequence[int(position)]
    except (IndexError, ValueError, TypeError):
        return None


def order_aware_result_list(cl):
    context = django_result_list(cl)
    if cl.opts.model_name == "order":
        context["order_row_list"] = [
            {"is_new": obj.is_new, "status": obj.status}
            for obj in cl.result_list
        ]
    return context


@register.tag(name="result_list")
def result_list_tag(parser, token):
    return InclusionAdminNode(
        parser,
        token,
        func=order_aware_result_list,
        template_name="change_list_results.html",
        takes_context=False,
    )
