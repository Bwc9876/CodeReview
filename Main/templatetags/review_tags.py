from django import template
from django.template.loader import render_to_string
from django.db.models import QuerySet

from Users.models import User
from Main.models import Review

register = template.Library()

formatters = {
    'student': lambda target_id:    str(User.objects.get(id=target_id)),
    'reviewer': lambda target_id:    str(User.objects.get(id=target_id)),
    'status': lambda target_code:   Review.get_status_from_string(target_code)
}


@register.filter(name="review_table")
def review_table(queryset: QuerySet, fields_str: str):
    fields = fields_str.split(",")
    actions = []
    for field in fields:
        if field in ["edit", "cancel", "claim", "abandon", "grade", "view"]:
            fields.remove(field)
            actions.append(field)
    objects = []
    for old_object in queryset.values_list(*fields, 'id'):
        new_object = []
        for index, field in enumerate(old_object):
            if index != len(old_object) - 1:
                new_object.append(formatters.get(fields[index], lambda x:   x)(field))
            else:
                new_object.append(field)
        objects.append(new_object)
    return render_to_string('reviews/review_table.html', {'objects': objects, 'actions': actions, 'fields': fields,
                                                          'colspan': len(fields) + len(actions)})
