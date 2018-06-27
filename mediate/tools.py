from django.db.models import Q
import re


def normalize_query(query_string,
    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
    normspace=re.compile(r'\s{2,}').sub):
    """
    Splits the query string in individual keywords, getting rid of unnecessary spaces 
    and grouping quoted words together.
    Example:
    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    :param query_string: 
    :param findterms: regex to find terms
    :param normspace: regex to normalize spaces
    :return: 
    """

    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


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
    words = normalize_query(value)
    for word in words:
        query_keywords = {name + '__' + lookup_expr: word}
        q = q | Q(**query_keywords)
    return queryset.filter(q)
