from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _

from django.conf import settings

from .models import Moderation, ModerationAction, ModerationState, register_model


def moderated(relevant_fields_list=[]):
    def decorator(cls):
        """
        Model class decorator to add an under_moderation method
        :param cls: the Model class
        :return: the extended Model class 
        """

        # First register this model
        register_model(cls)

        def under_moderation(self):
            """
            Method to check whether the object of this class in under moderation
            :return: boolean: whether the object of this class in under moderation
            """
            moderation = Moderation.objects.filter(object_pk=self.pk, state=ModerationState.PENDING.value)
            if moderation:
                return True
            else:
                return False
        cls.under_moderation = under_moderation

        # Filter relevant fields with existing class fields
        existing_class_fields = [f.name for f in cls._meta.fields]
        cls.relevant_fields = [f for f in relevant_fields_list if f in existing_class_fields]

        return cls
    return decorator


def moderate(action=None, check_under_moderation=True):
    def decorator(cls):
        """
        View class decorator for making a moderation 
        :param cls: the View class
        :return: the extende View class
        """
        if not settings.MODERATION_OFF:
            if DeleteView in cls.__bases__:
                moderation_action = action if action else ModerationAction.DELETE

                def delete(self, request, *args, **kwargs):
                    if not request.user.is_superuser:
                        self.object = self.get_object()
                        if self.object.under_moderation():
                            messages.add_message(self.request, messages.WARNING,
                                                 _("This object ({}) is already under moderation.").format(self.object))
                        else:
                            moderation = Moderation.create(editor=self.request.user, obj=self.object,
                                                           action=moderation_action)
                            moderation.save()
                            messages.add_message(self.request, messages.SUCCESS,
                                                 _("Your changes will be sent to a moderator for reviewing."))
                        return HttpResponseRedirect(self.get_success_url())
                    else:
                        return super().delete(request, *args, **kwargs)

                cls.delete = delete

            else:
                if action:
                    moderation_action = action
                elif CreateView in cls.__bases__:
                    moderation_action = ModerationAction.CREATE
                elif UpdateView in cls.__bases__:
                    moderation_action = ModerationAction.UPDATE
                else:
                    raise Exception(_("Could not determine moderation action "))

                if UpdateView in cls.__bases__:
                    # Check whether the object is under moderation when the update form is requested
                    if check_under_moderation:
                        def get(self, request, *args, **kwargs):
                            obj = self.get_object()
                            if obj.under_moderation():
                                messages.add_message(self.request, messages.WARNING,
                                                     _("This object ({}) is already under moderation.").format(obj))
                                return HttpResponseRedirect(self.get_success_url())
                            else:
                                return super(cls, self).get(request, *args, **kwargs)

                        cls.get = get

                # Create a form_valid method for both Create and Update
                def form_valid(self, form, *args, **kwargs):
                    if not self.request.user.is_superuser:
                        self.object = form.save(commit=False)
                        if self.object.under_moderation():
                            messages.add_message(self.request, messages.WARNING,
                                                 _("This object ({}) is already under moderation.").format(self.object))
                        else:
                            moderation = Moderation.create(editor=self.request.user, obj=self.object, action=moderation_action)
                            moderation.save()
                            messages.add_message(self.request, messages.SUCCESS,
                                                 _("Your changes will be sent to a moderator for reviewing."))
                        return HttpResponseRedirect(self.get_success_url())
                    else:
                        return super().form_valid(form, *args, **kwargs)

                cls.form_valid = form_valid

        return cls
    return decorator


class ModeratedCreateView(CreateView):
    def form_valid(self, form, *args, **kwargs):
        if not self.request.user.is_superuser and not settings.MODERATION_OFF:
            self.object = form.save(commit=False)
            if self.object.under_moderation():
                messages.add_message(self.request, messages.WARNING,
                                     _("This object ({}) is already under moderation.").format(self.object))
            else:
                moderation = Moderation.create(editor=self.request.user, obj=self.object,
                                               action=ModerationAction.CREATE)
                moderation.save()
                messages.add_message(self.request, messages.SUCCESS,
                                     _("Your changes will be sent to a moderator for reviewing."))
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super().form_valid(form, *args, **kwargs)
