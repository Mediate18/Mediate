from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

import uuid


class SourceMaterial(models.Model):
     """
     Source material
     """
     name = models.CharField(_("Source material name"), max_length=128)

     def __str__(self):
         return self.name


class Transcription(models.Model):
    """
    Transcription
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField(_("Creation date"))
    source_material = models.ForeignKey(SourceMaterial, on_delete=models.PROTECT)
    curator = models.CharField(_("Curator"), max_length=128)

    def __str__(self):
        return _("{} as transcribed by {}").format(self.source_material, self.author)


class DocumentScan(models.Model):
    """
    Document scan
    """
    transcription = models.ForeignKey(Transcription, on_delete=models.SET_NULL, null=True, related_name="scans")
    scan = models.FileField()

    def __str__(self):
        return self.scan.name