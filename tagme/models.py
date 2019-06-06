from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import uuid


class Tag(models.Model):
    namespace = models.CharField(max_length=128, null=True, blank=True)
    name = models.CharField(max_length=128)
    value = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        namespace_part = "{}:".format(self.namespace) if self.namespace else ""
        value_part = "={}".format(self.value) if self.value else ""
        return "{}{}{}".format(namespace_part, self.name, value_part)


class TaggedEntity(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, editable=False, on_delete=models.SET_NULL)
    if getattr(settings, 'TAGME_OBJECT_ID_TYPE', "") == "uuid":
        object_id = models.UUIDField(default=uuid.uuid4, null=True, editable=False)
    else:
        object_id = models.PositiveIntegerField(null=True, blank=True, editable=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = 'TaggedEntities'

    def __str__(self):
        return "{} {}: {}".format(self.content_type, self.object_id, self.tag)

# Enable the simple-history registration:
from .history import *
