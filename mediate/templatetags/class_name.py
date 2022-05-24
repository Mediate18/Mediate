from django.template import Library
from django.apps import apps


register = Library()


@register.filter
def get_object_class_name(obj):
    return obj.__class__._meta.verbose_name


@register.filter
def get_object_class_name_plural(obj):
    return obj.__class__._meta.verbose_name_plural


@register.filter
def get_class_name(class_name):
    app_name, model_name = class_name.split('__', 1)
    model = apps.get_model(app_label=app_name, model_name=model_name)
    return model._meta.verbose_name


@register.filter
def get_class_name_plural(class_name):
    app_name, model_name = class_name.split('__', 1)
    model = apps.get_model(app_label=app_name, model_name=model_name)
    return model._meta.verbose_name_plural