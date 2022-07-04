from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

import uuid

from persons.models import Place

from simplemoderation.tools import moderated


class SourceMaterial(models.Model):
    """
    Source material
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Source material name"), max_length=128)

    def __str__(self):
        return self.name


@moderated()
class Transcription(models.Model):
    """
    Transcription
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField(_("Creation date"), auto_now_add=True)
    source_material = models.ForeignKey(SourceMaterial, on_delete=models.PROTECT)
    curator = models.CharField(_("Curator"), max_length=128)

    class Meta:
        verbose_name = "shelf mark of transcribed copy"
        verbose_name_plural = "shelf mark of transcribed copies"

    def __str__(self):
        return _("{} as transcribed by {} ({})").format(self.source_material, self.author,
                                                      ", ".join([str(scan.scan) for scan in self.scans.all()]))

    def get_absolute_url(self):
        return reverse_lazy('transcription_detail', args=[str(self.uuid)])


class ShelfMark(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True)
    library = models.ForeignKey('catalogues.Library', on_delete=models.SET_NULL, null=True)
    text = models.CharField(_("Shelf mark"), max_length=128)

    def __str__(self):
        strs = []
        if self.place:
            strs.append(_("Place: {}").format(self.place))
        if self.library:
            strs.append(_("Library: {}").format(self.library))
        strs.append(_("Text: {}").format(self.text))
        strs.append(_("Collection(s): {}").format(", ".join(self.collection_set.all())))
        return "; ".join(strs)


class DocumentScan(models.Model):
    """
    Document scan
    """
    DOCUMENT_SCAN_FOLDER = 'document_scans'

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transcription = models.ForeignKey(Transcription, on_delete=models.SET_NULL, null=True, related_name="scans")
    shelf_mark = models.ForeignKey(ShelfMark, on_delete=models.SET_NULL, null=True)
    scan = models.FileField(upload_to=DOCUMENT_SCAN_FOLDER)


    def __str__(self):
        return self.scan.name

    def delete(self, using=None, keep_parents=False):
        # Prepare to move the scan file
        import os
        from django.conf import settings
        old_path = self.scan.path
        file_name = os.path.basename(old_path)
        new_folder = os.path.join(settings.MEDIA_ROOT, self.DOCUMENT_SCAN_FOLDER, 'deleted')
        os.makedirs(new_folder, exist_ok=True)
        new_path = os.path.join(new_folder, '{}_{}_{}'.format(self.__class__.__name__, self.uuid, file_name))

        # Delete the object
        super(DocumentScan, self).delete(using=using, keep_parents=keep_parents)

        # Move the scan file
        os.rename(old_path, new_path)


# Enable the simple-history registration:
from .history import *


# Clear cache when a model object is saved
from django.db.models.signals import post_save, post_delete
from mediate.tools import receiver_with_multiple_senders
from django.core.cache import cache


@receiver_with_multiple_senders([post_save, post_delete],[SourceMaterial, Transcription, DocumentScan])
def clear_cache(sender, instance, **kwargs):
    cache.clear()