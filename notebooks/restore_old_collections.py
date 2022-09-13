#!/usr/bin/env python
# coding: utf-8

# In[1]:


from django.db import transaction, IntegrityError

from catalogues.models import *
from items.models import *
from persons.models import *


# In[2]:


collection_names = [
    "Hjerm 1686",
    "Ulfborg 1687",
    "Hvidding 1690",
    "Hemmet 1693",
    "Hemmet (edit) 1685",
    "Campbell 1778",
    "Younge 1773",
    "Laugher 1782",
    "Paulmy 1758",
    "Rast 1812",
]


# In[3]:


collection_uuids = []
for name in collection_names:
#     print(name)
    collections = HistoricalCollection.objects.filter(short_title=name, history_type="-")
    if collections.count() == 1:
#         print(collections.first().uuid)
        collection_uuids.append((collections.first().short_title, collections.first().uuid))
    else:
        name= name.split()[0]
        collections = HistoricalCollection.objects.filter(short_title__startswith=name, history_type="-")
        if collections.count() == 1:
#             print(collections.first().uuid)
            collection_uuids.append((collections.first().short_title, collections.first().uuid))
        else:
            print(name, "has", collections.count(), "collections")
#     print()
    
print(collection_uuids)


# In[4]:


dump = Dataset.objects.get(name="Dump")


# In[5]:


CHANGE_DB = True


def save_instances(things):
    if CHANGE_DB:
        for thing in things:
            if not thing.next_record:
                thing.instance.save()


# In[6]:


get_ipython().run_line_magic('timeit', '')
# with transaction.atomic():
for short_title, uuid in collection_uuids:
    # Collection
    print("Collection:", short_title, uuid)
    collection = HistoricalCollection.objects.get(uuid=uuid, history_type="-").instance
    if CHANGE_DB:
        collection.save()

    # Catalogue
    if CHANGE_DB:
        catalogue, created = Catalogue.objects.get_or_create(name=short_title, dataset=dump)
        if created:
            print("Created", catalogue)
        collection.catalogue.add(catalogue)

    # Lots
    lots = HistoricalLot.objects.filter(collection_id=uuid, history_type="-")
    print("Lots:", lots.count())

    # Categories
    old_categories = HistoricalCategory.objects.filter(uuid__in=lots.values('category_id'), history_type="-")
    print("old Categories:", old_categories.count())
    if CHANGE_DB:
        save_instances(old_categories)

    existing_categories = Category.objects.filter(uuid__in=lots.values('category_id'))
    print("existing Categories:", existing_categories.count())
    if CHANGE_DB:
        existing_categories.update(collection=collection)

    save_instances(lots)

    # Items
    items = HistoricalItem.objects.filter(lot_id__in=lots.values('uuid'), history_type="-")
    print("Items:", items.count())  #, list(items.filter(book_format__isnull=False).values_list('book_format', flat=True)))

    # Book format
    book_formats = HistoricalBookFormat.objects.filter(uuid__in=items.values('book_format_id'), history_type="-")
    print("BookFormat:", book_formats.count())
    save_instances(book_formats)

    save_instances(items)

    # Editions
    editions = HistoricalEdition.objects.filter(uuid__in=items.values('edition_id'), history_type="-")
    print("Editions:", editions.count())
    save_instances(editions)

    # Edition Places
    edition_places = HistoricalPlace.objects.filter(uuid__in=editions.values('place_id'), history_type="-")
    print("Edition Places:", edition_places.count())
    save_instances(edition_places)

    # Publishers
    publishers = HistoricalPublisher.objects.filter(edition_id__in=editions.values('uuid'), history_type="-")
    print("Publishers:", publishers.count())

    # Publisher persons
    publisher_persons = HistoricalPerson.objects.filter(uuid__in=publishers.values('publisher_id'), history_type="-")
    print("Publisher persons:", publisher_persons.count())
    save_instances(publisher_persons)

    save_instances(publishers)

    # Item Persons
    item_persons = HistoricalPersonItemRelation.objects.filter(item_id__in=items.values('uuid'), history_type="-")
    print("PersonItemRelations:", item_persons.count())

    # Person Item Relation Role
    person_item_relation_roles = HistoricalPersonItemRelationRole.objects.filter(uuid__in=item_persons.values('role_id'), history_type="-")
    print("PersonItemRelationRoles:", person_item_relation_roles.count())
    save_instances(person_item_relation_roles)

    # Persons
    persons = HistoricalPerson.objects.filter(uuid__in=item_persons.values('person_id'), history_type="-")
    print("Persons:", persons.count())
    save_instances(persons)

    try:
        save_instances(item_persons)
    except IntegrityError:
        pass            

    # Item Works
    item_works = HistoricalItemWorkRelation.objects.filter(item_id__in=items.values('uuid'), history_type="-")
    print("ItemWorkRelations:", item_works.count())

    # Works
    works = HistoricalWork.objects.filter(uuid__in=item_works.values('work_id'), history_type="-")
    print("Works:", works.count())
    save_instances(works)
    
    save_instances(item_works)

    # Item Languages
    item_languages = HistoricalItemLanguageRelation.objects.filter(item_id__in=items.values('uuid'), history_type="-")
    print("ItemLanguageRelations:", item_languages.count())
    save_instances(item_languages)

    # Language
    languages = HistoricalLanguage.objects.filter(uuid__in=item_languages.values('language_id'), history_type="-")
    print("Languages:", languages.count())
    save_instances(languages)

    # Item Material
    item_materials = HistoricalItemMaterialDetailsRelation.objects.filter(item_id__in=items.values('uuid'), history_type="-")
    print("ItemMaterialDetailsRelation:", item_materials.count())

    # Material details
    material_details = HistoricalMaterialDetails.objects.filter(uuid__in=item_materials.values('material_details_id'), history_type="-")
    print("MaterialDetails:", material_details.count())
    save_instances(material_details)

    save_instances(item_materials)

    # Collection Persons
    collection_persons = HistoricalPersonCollectionRelation.objects.filter(collection_id=uuid, history_type="-")
    print("PersonCollectionRelations:", collection_persons.count())

    # Persons
    persons = HistoricalPerson.objects.filter(uuid__in=collection_persons.values('person_id'), history_type="-")
    print("Persons:", persons.count())
    save_instances(persons)

    save_instances(collection_persons)

    # Collection Places
    collection_places = HistoricalCollectionPlaceRelation.objects.filter(collection_id=uuid, history_type="-")
    print("CollectionPlaceRelation:", collection_places.count())

    # Places
    places = HistoricalPlace.objects.filter(uuid__in=collection_places.values('uuid'))
    print("Places:", places.count())
    save_instances(places)

    save_instances(collection_places)

    print()

# raise Exception

