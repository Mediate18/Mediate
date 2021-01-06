from django import forms
from django.db.models import Q, Count, QuerySet
import django_filters
from django_filters.constants import STRICTNESS
from django_filters.filters import Lookup

import six


class QBasedFilter:
    """
    Merely a super class for testing with isinstance.
    """
    pass


class QBasedFilterset(django_filters.FilterSet):
    # Override method
    @property
    def qs(self):
        if not hasattr(self, '_qs'):
            if not self.is_bound:
                self._qs = self.queryset.all()
                return self._qs

            if not self.form.is_valid():
                if self.strict == STRICTNESS.RAISE_VALIDATION_ERROR:
                    raise forms.ValidationError(self.form.errors)
                elif self.strict == STRICTNESS.RETURN_NO_RESULTS:
                    self._qs = self.queryset.none()
                    return self._qs
                # else STRICTNESS.IGNORE...  ignoring

            # start with all the results and filter from there
            qs = self.queryset.all()
            query = Q()
            for name, filter_ in six.iteritems(self.filters):
                if isinstance(filter_, QBasedFilter):
                    value = self.form.cleaned_data.get(name)

                    if value is not None:  # valid & clean data
                        query = filter_.filter(query, value)

            qs = qs.filter(query)

            for name, filter_ in six.iteritems(self.filters):
                if not isinstance(filter_, QBasedFilter):
                    value = self.form.cleaned_data.get(name)

                    if isinstance(value, QuerySet):
                        if value.exists():
                            qs = filter_.filter(qs, value)
                    elif value is not None:  # valid & clean data
                        qs = filter_.filter(qs, value)

            self._qs = qs.distinct()

        return self._qs


class RangeFilterQ(QBasedFilter, django_filters.RangeFilter):
    """
    Subclass of django_filters.RangeFilter for the purpose of
    using Q objects within one filter instead of chaining filters.
    """

    def filter(self, q, value):
        """RangeFilter filter method override for use of Q(...) """
        if value:
            if value.start is not None and value.stop is not None:
                lookup = '%s__range' % self.field_name
                return q & Q(**{lookup: (value.start, value.stop)})
            else:
                if value.start is not None:
                    q &= Q(**{'%s__gte' % self.field_name: value.start})
                if value.stop is not None:
                    q &= Q(**{'%s__lte' % self.field_name: value.stop})
        return q


class RangeRangeFilterQ(QBasedFilter, django_filters.RangeFilter):
    """
    Subclass of django_filters.RangeFilter for the purpose of
    using Q objects within one filter instead of chaining filters.

    Both the field and the filter are a range.
    """

    def __init__(self, *args, **kwargs):
        self.field_names = kwargs.pop('field_names', {})
        super().__init__(*args, **kwargs)

    def filter(self, q, value):
        """RangeFilter filter method override for use of Q(...) """
        if value:
            if value.start and not value.stop:
                q &= Q(**{'{}__gte'.format(self.field_names[0]): value.start}) \
                    | Q(**{'{}__gte'.format(self.field_names[1]): value.start})
            elif value.stop and not value.start:
                q &= Q(**{'{}__gte'.format(self.field_names[0]): value.stop}) \
                    | Q(**{'{}__gte'.format(self.field_names[1]): value.stop})
            else:  # value.start and value.end
                q &= Q(**{'{}__range'.format(self.field_names[0]): (value.start, value.stop)}) \
                     | Q(**{'{}__range'.format(self.field_names[1]): (value.start, value.stop)}) \
                     | (Q(**{'{}__lte'.format(self.field_names[0]): value.start}) & \
                        Q(**{'{}__gte'.format(self.field_names[1]): value.stop}))
        return q


class MultipleChoiceFilterQWithExtraLookups(QBasedFilter, django_filters.MultipleChoiceFilter):
    """
    Subclass of django_filters.MultipleChoiceFilter for the purpose of
    using Q objects within one filter instead of chaining filters.
    """

    def __init__(self, *args, **kwargs):
        self.extra_field_lookups = kwargs.pop('extra_field_lookups', {})
        super().__init__(*args, **kwargs)

    def filter(self, q, value):
        """MultipleChoiceFilter filter method override for use of Q(...) """
        if isinstance(value, Lookup):
            lookup = six.text_type(value.lookup_type)
            value = value.value
        else:
            lookup = self.lookup_expr
        if not value:
            return q
        q &= Q(**{'%s__%s' % (self.field_name, lookup): value, **self.extra_field_lookups})
        return q


class ModelMultipleChoiceFilterQ(QBasedFilter, django_filters.ModelMultipleChoiceFilter):
    """
    Subclass of django_filters.ModelMultipleChoiceFilter for the purpose of
    using Q objects within one filter instead of chaining filters.
    """

    def filter(self, q, value):
        """ModelMultipleChoiceFilter filter method override for use of Q(...) """
        if isinstance(value, Lookup):
            lookup = six.text_type(value.lookup_type)
            value = value.value
        else:
            lookup = self.lookup_expr
        if not value:
            return q
        q &= Q(**{'%s__%s' % (self.field_name, lookup): value})
        return q


class ModelMultipleChoiceFilterQWithExtraLookups(QBasedFilter, django_filters.ModelMultipleChoiceFilter):
    """
    Subclass of django_filters.MultipleChoiceFilter for the purpose of
    using Q objects within one filter instead of chaining filters.
    """

    def __init__(self, *args, **kwargs):
        self.extra_field_lookups = kwargs.pop('extra_field_lookups', {})
        super().__init__(*args, **kwargs)

    def filter(self, q, value):
        """MultipleChoiceFilter filter method override for use of Q(...) """
        if isinstance(value, Lookup):
            lookup = six.text_type(value.lookup_type)
            value = value.value
        else:
            lookup = self.lookup_expr
        if not value:
            return q
        q &= Q(**{'%s__%s' % (self.field_name, lookup): value, **self.extra_field_lookups})
        return q
