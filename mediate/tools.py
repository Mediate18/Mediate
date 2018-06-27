from django.db.models import Q


def filter_multiple_words(lookup_expr, queryset, name, value):
    """
    Filters the given queryset for each word in the given value, 
    using the name of a field and a lookup expression. 
    :param lookup_expr: a lookup expression, e.g. icontains
    :param queryset: a Django queryset
    :param name: the name of a field
    :param value: the value of that field
    :return: 
    """
    q = Q()
    words = value.split()
    for word in words:
        query_keywords = {name + '__' + lookup_expr: word}
        q = q | Q(**query_keywords)
    return queryset.filter(q)
