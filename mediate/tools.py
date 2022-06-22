from django.conf import settings
from django.db.models import Q, Func, Count
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


def wildcards_to_mysqlregex(wildcard_search_string):
    """
    Replaces each '?' to [[:alpha:]] which is the MySQL regex character class for alphabetical characters, and
    replaces each '*' to [[:alpha:]]+. 
    :param wildcard_search_string: 
    :return: 
    """
    mysqlregex = re.escape(wildcard_search_string)
    return mysqlregex.replace('?', '[[:alpha:]]').replace('*', '[[:alpha:]]+')


def filter_multiple_words(lookup_expr, queryset, name, value, wildcards=False):
    """
    Filters the given queryset for each word in the given value, 
    using the name of a field and a lookup expression. 
    :param lookup_expr: a lookup expression, e.g. icontains
    :param queryset: a Django queryset
    :param name: the name of a field
    :param value: the value of that field
    :return: 
    """
    if wildcards:
        lookup_expr = 'iregex'

    q = Q()
    words = normalize_query(value)
    for word in words:
        if wildcards:
            word = wildcards_to_mysqlregex(word)
        query_keywords = {name + '__' + lookup_expr: word}
        q = q | Q(**query_keywords)
    return queryset.filter(q)


def put_layout_in_context(original_get_context_data_function):
    """
    A decorator function to add the GET request variable 'layout' to the context.
    Works on get_context_data methods of class based views.
    :param original_get_context_data_function: the original get_context_data function
    :return: get_context_data_with_layout: the wrapper function
    """

    def get_context_data_with_layout(self, *args, **kwargs):
        context = original_get_context_data_function(self, *args, **kwargs)
        # if 'layout' in self.request.GET and self.request.GET['layout'] == 'bare':
        #     context['extended_layout'] = 'barelayout.html'
        layout = self.request.GET.get('layout')
        if layout and layout in settings.AVAILABLE_LAYOUTS:
            context['extended_layout'] = "{}{}".format(layout, settings.LAYOUT_SUFFIX)
        return context
    return get_context_data_with_layout


def put_get_variable_in_context(mapping):
    """
    A decorator function to add a GET request variable to the context.
    Works on get_context_data methods of class based views.
    :param mapping: a tuple/list of 2-tuple with the get request variable and the context key
    :return: the wrapping function
    """
    def wrapper(original_get_context_data_function):
        """
        The actual function wrapper
        :param original_get_context_data_function: the original get_context_data function 
        :return: 
        """
        def get_context_data_with_get_variable(self, *args, **kwargs):
            context = original_get_context_data_function(self, *args, **kwargs)
            for pair in mapping:
                if pair[1] not in context and pair[0] in self.request.GET:
                    context[pair[1]] = self.request.GET.get(pair[0])
            return context
        return get_context_data_with_get_variable
    return wrapper


def receiver_with_multiple_senders(signal, senders, **kwargs):
    """
    Based on django.dispatch.dispatcher.receiver

    Allows multiple senders so we can avoid using a stack of
    regular receiver decorators with one sender each.
    """

    def decorator(receiver_func):
        for sender in senders:
            if isinstance(signal, (list, tuple)):
                for s in signal:
                    s.connect(receiver_func, sender=sender, **kwargs)
            else:
                signal.connect(receiver_func, sender=sender, **kwargs)

        return receiver_func

    return decorator