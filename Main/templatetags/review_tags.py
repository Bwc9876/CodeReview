from django import template
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.db.models import QuerySet
from django.template.context_processors import csrf

from Users.models import User
from Main.models import Review

register = template.Library()

formatters = {
    'student': lambda target_id:    str(User.objects.get(id=target_id)),
    'reviewer': lambda target_id:    str(User.objects.get(id=target_id)),
    'status': lambda target_code:   Review.get_status_from_string(target_code)
}


@register.simple_tag(name="review_table")
def review_table(queryset: QuerySet, fields_str: str, request=None):
    fields = []
    actions = []
    for field in fields_str.split(","):
        if field in ["edit", "cancel", "claim", "abandon", "grade", "view"]:
            actions.append(field)
        else:
            fields.append(field)
    objects = []
    for old_object in queryset.values_list(*fields, 'id'):
        new_object = []
        for index, field in enumerate(old_object):
            if index != len(old_object) - 1:
                new_object.append(formatters.get(fields[index], lambda x:   x)(field))
            else:
                new_object.append(field)
        objects.append(new_object)
    context = {'objects': objects, 'actions': actions,
               'fields': fields, 'colspan': len(fields) + len(actions),
               'csrf_token': "" if request is None else csrf(request)['csrf_token'] }
    return render_to_string('reviews/review_table.html', context)
