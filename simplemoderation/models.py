from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
import uuid
from enum import Enum

from .fields import SerializedObjectField


class ModerationAction(Enum):
    CREATE = "C"
    UPDATE = "U"
    DELETE = "D"


class ModerationState(Enum):
    PENDING = "P"
    APPROVED = "A"
    REJECTED = "R"


class Moderation(models.Model):
    """
    
    """
    # The action
    editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="moderated_objects",
                               editable=False)
    created_datetime = models.DateTimeField(auto_now_add=True, editable=False)
    action = models.CharField(max_length=1, choices=[(tag.value, tag) for tag in ModerationAction], default='C',
                              editable=False)

    # The created/updated/deleted object
    data = SerializedObjectField(serialize_format='json', editable=False)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, editable=False, on_delete=models.SET_NULL)
    if getattr(settings, 'MODERATED_OBJECT_PK', "") == "use_uuid":
        object_pk = models.UUIDField(default=uuid.uuid4, null=True, editable=False)
    else:
        object_pk = models.PositiveIntegerField(null=True, blank=True, editable=False)
    content_object = GenericForeignKey('content_type', 'object_pk')

    # The moderation
    # The moderation that this moderation is dependent on:
    master = models.ForeignKey('Moderation', null=True, blank=True, on_delete=models.SET_NULL)
    state = models.CharField(max_length=1, choices=[(tag.value, tag) for tag in ModerationState], default='P')
    moderated_datetime = models.DateTimeField(null=True)
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="handled_moderations")
    reason = models.TextField(blank=True)

    @staticmethod
    def create(editor, obj, action):
        return Moderation(
                    editor=editor,
                    action=action.value,
                    object_pk=obj.pk,
                    data=obj,
                    content_type=ContentType.objects.get_for_model(obj)
                )
