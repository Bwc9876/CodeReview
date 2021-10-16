from django import template
from django.db.models import QuerySet
from django.core.paginator import Page

from Main.models import Review
from Users.models import User

register = template.Library()

formatters = {
    'student': lambda target_id: str(User.objects.get(id=target_id)),
    'reviewer': lambda target_id: str(User.objects.get(id=target_id)),
    'status': lambda target_code: Review.get_status_from_string(target_code)
}


def get_table_context(queryset: QuerySet, fields_str: str):
    fields = []
    actions = []
    for field in fields_str.split(","):
        if field in ["edit", "cancel", "claim", "abandon", "grade", "view", "delete"]:
            actions.append(field)
        else:
            fields.append(field)
    objects = []
    for old_object in queryset.values_list(*fields, 'id'):
        new_object = []
        for index, field in enumerate(old_object):
            if index != len(old_object) - 1:
                new_object.append(formatters.get(fields[index], lambda x: x)(field))
            else:
                new_object.append(field)
        objects.append(new_object)
    return {'objects': objects, 'actions': actions, 'fields': fields, 'colspan': len(fields) + len(actions)}


@register.inclusion_tag('reviews/review_table.html')
def review_table(queryset: QuerySet, fields_str: str):
    return get_table_context(queryset, fields_str)


@register.inclusion_tag('reviews/review_completed_preview_table.html')
def review_complete_preview_table(queryset: QuerySet, fields_str: str, session: str = None):
    new_context = get_table_context(queryset[:4], fields_str)
    if queryset.count() > 4:
        new_context['target_session'] = session
        return new_context
    else:
        new_context['hide_view_all'] = True
        return new_context


@register.filter()
def get_session(queryset: QuerySet, session: str):
    return queryset.filter(student__session=session)
