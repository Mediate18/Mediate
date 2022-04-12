from simple_history import register
from .models import *


register(Dataset)
register(Collection_TMP)
register(Collection_TMPYear)
register(CatalogueType)
register(Library)
register(Catalogue)
register(CatalogueCatalogueTypeRelation)
register(CatalogueHeldBy)
register(Lot)
register(PersonCollection_TMPRelation)
register(PersonCatalogueRelationRole)
register(PersonCatalogueRelation)
register(CataloguePlaceRelation)
register(ParisianCategory)
register(Category)
