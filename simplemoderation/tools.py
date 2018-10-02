from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _

from .models import Moderation, ModerationAction


def under_moderation(cls):
    """
    Model class decorator to add an under_moderation method
    :param cls: the Model class
    :return: the extended Model class 
    """
    def under_moderation(self):
        """
        Method to check whether the object of this class in under moderation
        :return: boolean: whether the object of this class in under moderation
        """
        moderation = Moderation.objects.filter(object_pk=self.pk, state='P')
        if moderation:
            return True
        else:
            return False
    cls.under_moderation = under_moderation

    return cls


def moderate(cls):
    """
    View class decorator for making a moderation 
    :param cls: the View class
    :return: the extende View class
    """

    if DeleteView in cls.__bases__:
        action = ModerationAction.DELETE

        def delete(self, request, *args, **kwargs):
            if not request.user.is_superuser:
                self.object = self.get_object()
                if self.object.under_moderation():
                    messages.add_message(self.request, messages.WARNING,
                                         _("This object ({}) is already under moderation.").format(self.object))
                else:
                    moderation = Moderation.create(editor=self.request.user, obj=self.object,
                                                   action=action)
                    moderation.save()
                    messages.add_message(self.request, messages.SUCCESS,
                                         _("Your changes will be sent to a moderator for reviewing."))
                return redirect(self.get_success_url())
            else:
                return super().delete(request, *args, **kwargs)

        cls.delete = delete

        return cls

    else:
        if CreateView in cls.__bases__:
            action = ModerationAction.CREATE
        elif UpdateView in cls.__bases__:
            action = ModerationAction.UPDATE

            def get(self, request, *args, **kwargs):
                obj = self.get_object()
                if obj.under_moderation():
                    messages.add_message(self.request, messages.WARNING,
                                         _("This object ({}) is already under moderation.").format(obj))
                    return redirect(self.get_success_url())
                else:
                    return super().get(request, *args, **kwargs)

            cls.get = get

        # Create a form_valid method for both Create and Update
        def form_valid(self, form, *args, **kwargs):
            if not self.request.user.is_superuser:
                self.object = form.save(commit=False)
                if self.object.under_moderation():
                    messages.add_message(self.request, messages.WARNING,
                                         _("This object ({}) is already under moderation.").format(self.object))
                else:
                    moderation = Moderation.create(editor=self.request.user, obj=self.object, action=action)
                    moderation.save()
                    messages.add_message(self.request, messages.SUCCESS,
                                         _("Your changes will be sent to a moderator for reviewing."))
                return redirect(self.get_success_url())
            else:
                return super().form_valid(form, *args, **kwargs)

        cls.form_valid = form_valid

        return cls
