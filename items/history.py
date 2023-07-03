from simple_history import register
from .models import *


register(Language)
register(BookFormat)
register(MaterialDetails)
register(Subject)
register(Work)
register(WorkSubject)
register(WorkAuthor)
# register(Item)
register(ItemType)
register(ItemItemTypeRelation)
register(ItemAuthor)
register(ItemLanguageRelation)
register(ItemWorkRelation)
register(ItemMaterialDetailsRelation)
register(Edition)
register(Publisher)
register(PersonItemRelationRole)
register(PersonItemRelation)
