"""
    This file provides tags related to reviews to templates
"""

from django import template
from django.db.models import QuerySet

from Main.models import Review
from Users.models import User

register = template.Library()

formatters = {
    'student': lambda target_id: str(User.objects.get(id=target_id)),
    'reviewer': lambda target_id: str(User.objects.get(id=target_id)),
    'status': lambda target_code: Review.get_status_from_string(target_code)
}


def get_table_context(queryset: QuerySet, fields_str: str) -> dict:
    """
        This is a helper function that gets a set of Reviews ready to display in a table

        :param queryset: The Reviews to prepare
        :type queryset: QuerySet
        :param fields_str: The fields to get
        :type fields_str: str
        :returns: A dictionary that will work as context to render a table
        :rtype: dict
    """

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
def review_table(queryset: QuerySet, fields_str: str) -> dict:
    """
        This tag displays a QuerySet of reviews as a table

        :param queryset: The set of Reviews to display
        :type queryset: QuerySet
        :param fields_str: The fields to get for each review
        :type fields_str: str
        :returns: The reviews as a table
        :rtype: str
    """

    return get_table_context(queryset, fields_str)


@register.inclusion_tag('reviews/review_completed_preview_table.html')
def review_complete_preview_table(queryset: QuerySet, fields_str: str, session: str = None) -> dict:
    """
        This tag functions identically to review_table except one key difference,
        It limits it to the first 4 reviews and adds a "View All" link if the list is longer than that

        :param queryset: The set of Reviews to display
        :type queryset: QuerySet
        :param fields_str: The fields to get for each review
        :type fields_str: str
        :param session: The session the Reviews are in (if applicable)
        :type session: str
        :returns: The reviews as a table
        :rtype: str
    """

    new_context = get_table_context(queryset[:4], fields_str)
    if queryset.count() > 4:
        new_context['target_session'] = session
        return new_context
    else:
        new_context['hide_view_all'] = True
        return new_context


@register.filter()
def get_session(queryset: QuerySet, session: str) -> QuerySet:
    """
        This function takes a QuerySet of reviews and gets all Reviews with the specified session

        :param queryset: The set of Reviews to search
        :type queryset: QuerySet
        :param session: The session to search for
        :type session: str
        :returns: A subset of the given set that only contains Reviews in the given session
        :rtype: QuerySet
    """

    return queryset.filter(student__session=session)
