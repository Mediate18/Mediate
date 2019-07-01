from simple_history import register
from .models import *


register(Collection)
register(CollectionYear)
register(CatalogueType)
register(Library)
register(Catalogue)
register(CatalogueCatalogueTypeRelation)
register(CatalogueHeldBy)
register(Lot)
register(PersonCollectionRelation)
register(PersonCatalogueRelationRole)
register(PersonCatalogueRelation)
register(CataloguePlaceRelation)
register(ParisianCategory)
register(Category)
