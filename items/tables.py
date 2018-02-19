import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from items.models import Catalogue


class CatalogueTable(tables.Table):
    short_title = tables.LinkColumn('catalogue_detail', args=[A('pk')])

    class Meta:
        model = Catalogue
        fields = ('short_title', 'full_title', 'preface_and_paratexts', 'type', 'year_of_publication',
                    'terminus_post_quem', 'collection')