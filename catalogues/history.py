from simple_history import register
from .models import *


register(Dataset)
register(Catalogue)
register(CatalogueYear)
register(CollectionType)
register(Library)
register(Collection)
register(CollectionCollectionTypeRelation)
register(CollectionHeldBy)
register(Lot)
register(PersonCatalogueRelation)
register(PersonCollectionRelationRole)
register(PersonCollectionRelation)
register(CollectionPlaceRelation)
register(ParisianCategory)
register(Category)
