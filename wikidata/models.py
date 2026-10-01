from django.conf import settings
from django.db import models


class Wikidata(models.Model):
    wikidata_id = models.CharField(max_length=256, blank=True)

    class Meta:
        abstract = True

    def wikidata_url(self):
        return settings.WIKIDATA_URL.format(self.wikidata_id)